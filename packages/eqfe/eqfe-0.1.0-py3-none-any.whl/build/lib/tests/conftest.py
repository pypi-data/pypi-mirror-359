"""
Test Configuration and Utilities
"""

import pytest
import numpy as np


@pytest.fixture
def standard_env_params():
    """Standard environmental parameters for testing."""
    return {
        "field_mass": 1e-6,
        "coupling_strength": 1e-3,
        "temperature": 300.0,
    }


@pytest.fixture
def test_tolerances():
    """Standard tolerances for numerical tests."""
    return {"physics_bound": 1e-10, "numerical": 1e-12, "statistical": 0.1}


def assert_physics_compliant(S_value, tolerance=1e-10):
    """Assert that CHSH parameter respects physics bounds."""
    tsirelson_bound = 2 * np.sqrt(2)
    assert S_value <= tsirelson_bound + tolerance
