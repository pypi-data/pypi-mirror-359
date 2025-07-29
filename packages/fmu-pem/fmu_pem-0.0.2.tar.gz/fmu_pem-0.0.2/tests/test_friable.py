from unittest.mock import MagicMock

import numpy as np
import pytest

from fmu.pem.pem_functions.run_friable_model import run_friable
from fmu.pem.pem_utilities import (
    EffectiveFluidProperties,
    MatrixProperties,
    PemConfig,
    PressureProperties,
    SaturatedRockProperties,
)


@pytest.fixture
def valid_mineral():
    return MatrixProperties(
        bulk_modulus=np.ma.array([37e9, 37e9, 37e9], mask=[False, False, False]),
        shear_modulus=np.ma.array([44e9, 44e9, 44e9], mask=[False, False, False]),
        dens=np.ma.array([2650.0, 2650.0, 2650.0], mask=[False, False, False]),
    )


@pytest.fixture
def invalid_fluid():
    return np.ma.array([2.2e9, 2.2e9, 2.2e9], mask=[False, False, False])


@pytest.fixture
def valid_fluid():
    return EffectiveFluidProperties(
        bulk_modulus=np.ma.array([2.2e9, 2.2e9, 2.2e9], mask=[False, False, False]),
        dens=np.ma.array([1000.0, 1000.0, 1000.0], mask=[False, False, False]),
    )


@pytest.fixture
def valid_porosity():
    return np.ma.array([0.2, 0.25, 0.3], mask=[False, False, False])


@pytest.fixture
def valid_pressure():
    return PressureProperties(
        effective_pressure=np.ma.array([100, 150, 200], mask=[False, False, False]),
        formation_pressure=np.ma.array([50, 75, 100], mask=[False, False, False]),
        overburden_pressure=np.ma.array([200, 250, 300], mask=[False, False, False]),
    )


@pytest.fixture
def valid_config_mock():
    config_mock = MagicMock(spec=PemConfig)

    # Mocking the nested structure
    config_mock.rock_matrix = MagicMock()
    config_mock.rock_matrix.model.parameters = MagicMock()

    # Setting the attributes
    config_mock.rock_matrix.model.parameters.critical_porosity = 0.4
    config_mock.rock_matrix.model.parameters.coord_num_function.fcn = "PorBased"
    config_mock.rock_matrix.model.parameters.coordination_number = 9
    config_mock.rock_matrix.model.parameters.shear_reduction = 0.5

    return config_mock


@pytest.fixture
def valid_fluid_list():
    return [
        EffectiveFluidProperties(
            bulk_modulus=np.ma.array([2.2e9, 2.2e9, 2.2e9], mask=[False, False, False]),
            dens=np.ma.array([1000.0, 1000.0, 1000.0], mask=[False, False, False]),
        ),
        EffectiveFluidProperties(
            bulk_modulus=np.ma.array([2.0e9, 2.0e9, 2.0e9], mask=[False, False, False]),
            dens=np.ma.array([1020.0, 1020.0, 1020.0], mask=[False, False, False]),
        ),
    ]


@pytest.fixture
def valid_pressure_list():
    return [
        PressureProperties(
            effective_pressure=np.ma.array([100, 150, 200], mask=[False, False, False]),
            formation_pressure=np.ma.array([55, 80, 105], mask=[False, False, False]),
            overburden_pressure=np.ma.array(
                [210, 260, 310], mask=[False, False, False]
            ),
        ),
        PressureProperties(
            effective_pressure=np.ma.array([110, 160, 210], mask=[False, False, False]),
            formation_pressure=np.ma.array([60, 85, 110], mask=[False, False, False]),
            overburden_pressure=np.ma.array(
                [220, 270, 320], mask=[False, False, False]
            ),
        ),
    ]


def test_run_friable_valid_input(
    valid_mineral, valid_fluid, valid_porosity, valid_pressure, valid_config_mock
):
    """Test run_friable with valid inputs."""
    results = run_friable(
        valid_mineral, valid_fluid, valid_porosity, valid_pressure, valid_config_mock
    )
    assert isinstance(results, list)
    assert all(isinstance(item, SaturatedRockProperties) for item in results)


def test_run_friable_invalid_input_type(
    valid_mineral, valid_porosity, valid_pressure, valid_config_mock, invalid_fluid
):
    """Test run_friable with invalid input types to ensure it raises a ValueError."""
    with pytest.raises(ValueError):
        run_friable(
            valid_mineral,
            invalid_fluid,
            valid_porosity,
            valid_pressure,
            valid_config_mock,
        )


def test_run_friable_invalid_masked_array(
    valid_mineral, valid_porosity, valid_pressure, valid_config_mock
):
    invalid_fluid = EffectiveFluidProperties(
        bulk_modulus=np.ma.array([2.2e9, 2.2e9, 2.2e9], mask=[True, True, True]),
        dens=np.ma.array([1000, 1000, 1000], mask=[True, True, True]),
    )
    with pytest.raises(ValueError):
        run_friable(
            valid_mineral,
            invalid_fluid,
            valid_porosity,
            valid_pressure,
            valid_config_mock,
        )


def test_run_friable_list_fluid_and_pressure(
    valid_mineral,
    valid_fluid_list,
    valid_porosity,
    valid_pressure_list,
    valid_config_mock,
):
    """Test run_friable with list of fluids and pressures."""
    results = run_friable(
        valid_mineral,
        valid_fluid_list,
        valid_porosity,
        valid_pressure_list,
        valid_config_mock,
    )
    assert isinstance(results, list)
    assert all(isinstance(item, SaturatedRockProperties) for item in results)
