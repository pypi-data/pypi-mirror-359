from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from numpy.ma import MaskedArray


# Eclipse simulator file classes - SimInitProperties and time step SimRstProperties
@dataclass
class SimInitProperties:
    poro: MaskedArray
    depth: MaskedArray
    ntg: MaskedArray
    ntg_pem: Optional[MaskedArray] = None

    @property
    def delta_z(self) -> MaskedArray:
        """Estimate delta depth in the vertical direction"""

        def _verify_delta_z(inp_arr: MaskedArray) -> None:
            if not isinstance(inp_arr, MaskedArray) or inp_arr.dtype.kind != "f":
                raise TypeError(
                    f"input to estimate_delta_z must be a 3D numpy masked "
                    f"array with float data, is {type(inp_arr)}."
                )
            if np.ndim(inp_arr) != 3:
                raise ValueError(
                    f"{__file__}: 3-dimensional array must be input to "
                    f"estimate_delta_z. Depth difference is calculated along the "
                    f"third axis"
                )
            return

        _verify_delta_z(self.depth)
        d_z = np.zeros_like(self.depth)
        d_z[:, :, 1:] = self.depth.data[:, :, 1:] - self.depth.data[:, :, 0:-1]
        d_z[...] = np.clip(d_z, 0.0, a_max=None)
        delta_z: MaskedArray = MaskedArray(d_z, mask=self.depth.mask)
        return delta_z


@dataclass
class SimRstProperties:
    swat: MaskedArray
    sgas: MaskedArray
    soil: MaskedArray
    rs: MaskedArray
    pressure: MaskedArray
    temp: MaskedArray | None = None
    rv: MaskedArray | None = None
    salt: MaskedArray | None = None


# Elastic properties for matrix, i.e. mixed minerals and volume fractions
@dataclass
class MatrixProperties:
    bulk_modulus: MaskedArray
    shear_modulus: MaskedArray
    dens: MaskedArray


# Separate class for dry rock, i.e. with porosity, can use MatrixProperties as base
# class
@dataclass
class DryRockProperties(MatrixProperties):
    pass


# Acoustic properties for mixed fluids. If non-Newtonian fluids are to be considered,
# shear modulus and vs must be added
@dataclass
class EffectiveFluidProperties:
    bulk_modulus: MaskedArray
    dens: MaskedArray

    @property
    def vp(self):
        return np.sqrt(self.bulk_modulus / self.dens)


# Pressure properties - overburden, formation and effective (strictly speaking
# differential) pressure
@dataclass
class PressureProperties:
    formation_pressure: MaskedArray
    effective_pressure: MaskedArray
    overburden_pressure: MaskedArray


# Seismic two-way time
@dataclass
class TwoWayTime:
    twtpp: MaskedArray
    twtss: MaskedArray
    twtps: MaskedArray


# For isotropic elastic properties, only three independent components are needed
# to be defined, others can be derived from them, but this construction is needed
# to have all properties recognised by dataclasses.asdict()
@dataclass
class SaturatedRockProperties:
    vp: MaskedArray
    vs: MaskedArray
    dens: MaskedArray
    ai: MaskedArray = field(init=False)
    si: MaskedArray = field(init=False)
    vpvs: MaskedArray = field(init=False)

    def __post_init__(self):
        self.ai = self.vp * self.dens
        self.si = self.vs * self.dens
        self.vpvs = self.vp / self.vs
