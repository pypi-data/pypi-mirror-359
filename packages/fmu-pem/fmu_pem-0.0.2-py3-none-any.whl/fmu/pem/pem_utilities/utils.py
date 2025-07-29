import os
from contextlib import contextmanager
from pathlib import Path
from typing import List, Optional, Tuple, Union

import numpy as np
import xtgeo

from .pem_class_definitions import MatrixProperties
from .pem_config_validation import PemConfig


@contextmanager
def restore_dir(path: Path) -> None:
    """restore_dir run block of code from a given path, restore original path

    Args:
        path: path where the call is made from

    Returns:
        None
    """
    old_pwd = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_pwd)


def to_masked_array(
    value: Union[float, int], masked_array: np.ma.MaskedArray
) -> np.ma.MaskedArray:
    """Create a masked array with a constant value from an int or float and a template
    masked array

    Args:
        value: constant value for the returned masked array
        masked_array: template for shape and mask of returned masked array

    Returns:
        constant value masked array
    """
    return np.ma.MaskedArray(value * np.ones_like(masked_array), mask=masked_array.mask)


def filter_and_one_dim(
    *args: np.ma.MaskedArray, return_numpy_array: bool = False
) -> tuple[np.ma.MaskedArray, ...]:
    """Filters multiple masked arrays by removing masked values and flattens them to 1D.

    Typically used in preparation for calling the rock-physics library.

    Args:
        *args: One or more masked arrays of identical shape. Each array contains data
            with some values potentially masked as invalid.
        return_numpy_array: If True, returns regular numpy arrays instead of
            masked arrays for the filtered data. Defaults to False.

    Returns:
        tuple containing:
            - mask: Boolean array of the same shape as inputs where True indicates
              positions that were masked in any of the input arrays
            - filtered arrays: One or more 1D arrays containing only the unmasked values
              from each input array, in their original order
    """
    if not np.all([isinstance(arg, np.ma.MaskedArray) for arg in args]):
        raise ValueError(f"{__file__}: all inputs should be numpy masked arrays")
    mask = args[0].mask
    for i in range(1, len(args)):
        mask = np.logical_or(mask, args[i].mask)
    if return_numpy_array:
        out_args = [arg[~mask].data for arg in args]
    else:
        out_args = [arg[~mask] for arg in args]
    return mask, *out_args


def reverse_filter_and_restore(
    mask: np.ndarray, *args: np.ndarray
) -> Tuple[np.ma.MaskedArray, ...]:
    """Restores 1D filtered arrays back to their original shape with masking.

    Typically called with results returned from the rock-physics library.

    Args:
        mask: Boolean array where True indicates positions that should be masked
            in the restored arrays.
        *args: One or more 1D numpy arrays containing the filtered values to be
            restored. Each array should contain exactly enough values to fill
            the unmasked positions in the mask.

    Returns:
        tuple of masked arrays where:
            - Each array has the same shape as the input mask
            - Unmasked positions contain values from the input args
            - Masked positions (where mask is True) contain zeros and are masked
            - All returned arrays share the same mask
    """
    out_args: list[np.ma.MaskedArray] = []
    for arg in args:
        tmp = np.zeros(mask.shape)
        tmp[~mask] = arg
        out_args.append(np.ma.MaskedArray(tmp, mask=mask))

    return tuple(out_args)


def _verify_export_inputs(props, grid, dates, file_format=None):
    if file_format is not None and file_format not in ["roff", "grdecl"]:
        raise ValueError(
            f'{__file__}: output file format must be one of "roff", "grdecl", is '
            f"{file_format}"
        )
    if not isinstance(grid, xtgeo.grid3d.Grid):
        raise ValueError(
            f"{__file__}: model grid is not an xtgeo 3D grid, type: {type(grid)}"
        )
    if isinstance(props, list):
        if isinstance(dates, list):
            if len(props) == len(dates):
                return props, dates
            raise ValueError(
                f"{__file__}: length of property list does not match the number of "
                f"simulation model "
                f"dates: {len(props)} vs. {len(dates)}"
            )
        if dates is None:
            return props, [""] * len(props)
        raise ValueError(
            f"{__file__}: unknown input type, time_steps should be None or list, is "
            f"{type(dates)}"
        )
    if isinstance(props, dict):
        props = [
            props,
        ]
        if dates is None:
            return props, [
                "",
            ]
        if isinstance(dates, list) and len(dates) == 1:
            return props, dates
        raise ValueError(
            f"{__file__}: single length property list does not match the number of "
            f"simulation model "
            f"dates: {len(dates)}"
        )
    raise ValueError(
        f"{__file__}: unknown input types, result_props should be list or dict, is "
        f"{type(props)}, time_steps should be None or list, is {type(dates)}"
    )


def ntg_to_shale_fraction(
    ntg: np.ma.MaskedArray, por: np.ma.MaskedArray
) -> np.ma.MaskedArray:
    """Calculate sand and shale fraction from N/G property

    Args:
        ntg: net-to-gross property [fraction]
        por: total porosity [fraction]

    Returns:
        shale fraction
    """
    clip_ntg: np.ma.MaskedArray = np.ma.clip(np.ma.MaskedArray(ntg), 0.0, 1.0)  # type: ignore[assignment]
    vsh: np.ma.MaskedArray = np.ma.MaskedArray(1.0 - clip_ntg)
    return (vsh / (1.0 - por)).clip(0.0, 1.0)


def get_shale_fraction(
    vol_fractions: List[np.ma.MaskedArray],
    fraction_names: list[str],
    shale_fraction_names: Optional[str | list[str]],
) -> Optional[np.ma.MaskedArray]:
    """

    Args:
        vol_fractions: volume fractions, already verified that there is consistency
            between named fractions and available fractions in property file
        fraction_names: names of the volume fractions
        shale_fraction_names: Names of fractions that should be considered shale

    Returns:
        sum of volume fractions that are defined as shale, None if there are no defined
            shale fractions
    """

    if not shale_fraction_names:
        return None

    if isinstance(shale_fraction_names, str):
        shale_fraction_names = [shale_fraction_names]

    sh_list: list[np.ma.MaskedArray] = []
    for shale_name in shale_fraction_names:
        try:
            idx = fraction_names.index(shale_name)
            sh_list.append(vol_fractions[idx])
        except ValueError:
            raise ValueError(f"unknown shale fraction: {shale_name}")

    # Note that masked elements are set to 0 internally.
    return np.ma.sum(sh_list, axis=0)


def estimate_cement(
    bulk_modulus: float | int,
    shear_modulus: float | int,
    density: float | int,
    grid: np.ma.MaskedArray,
) -> MatrixProperties:
    """Creates masked arrays filled with constant cement properties, matching the shape
    and mask of the input grid.

    Args:
        bulk_modulus: Bulk modulus of the cement
        shear_modulus: Shear modulus of the cement
        density: Density of the cement
        grid: Template array that defines the shape and mask for the output arrays

    Returns:
        cement properties as MatrixProperties containing constant-valued masked arrays
    """
    cement_k = to_masked_array(bulk_modulus, grid)
    cement_mu = to_masked_array(shear_modulus, grid)
    cement_rho = to_masked_array(density, grid)
    return MatrixProperties(
        bulk_modulus=cement_k, shear_modulus=cement_mu, dens=cement_rho
    )


def update_dict_list(base_list: List[dict], add_list: List[dict]) -> List[dict]:
    """Update/add new key/value pairs to dicts in list

    Args:
        base_list: original list of dicts
        add_list: list of dicts to be added

    Returns:
        combined list of dicts
    """
    _verify_update_inputs(base_list, add_list)
    for i, item in enumerate(add_list):
        base_list[i].update(item)
    return base_list


def _verify_update_inputs(base, add_list):
    if not isinstance(base, list) and isinstance(add_list, list):
        raise TypeError(f"{__file__}: inputs are not lists")
    if not len(base) == len(add_list):
        raise ValueError(
            f"{__file__}: mismatch in list lengths: base list: {len(base)} vs. added "
            f"list: {len(add_list)}"
        )
    if not (
        all(isinstance(item, dict) for item in base)
        and all(isinstance(item, dict) for item in add_list)
    ):
        raise TypeError(f"{__file__}: all items in input lists are not dict")
