"""Tests for elevator_model module with 100% coverage."""

import numpy as np
import pytest
from src.elevator_model import ElevatorMDOFModel


@pytest.fixture
def default_params():
    """Default elevator parameters."""
    return {
        "m_motor": 198.45,
        "m_traction": 2835,
        "m_car_frame": 2282,
        "m_cabin": 1805,
        "m_counterweight": 4887.4,
        "k_rope_car": 2.72e5,
        "k_rope_counter": 2.72e5,
        "k_isolation": 9.8e5,
        "rope_stiffness": 1.176e11,
        "c_rope_car": 1000,
        "c_rope_counter": 1000,
        "c_isolation": 2000,
        "damping": 500,
    }


def test_model_initialization(default_params):
    """Test model initialization."""
    model = ElevatorMDOFModel(default_params)
    assert model.params == default_params
    assert model.M.shape == (6, 6)
    assert model.K.shape == (6, 6)
    assert model.C.shape == (6, 6)


def test_mass_matrix_assembly(default_params):
    """Test mass matrix assembly."""
    model = ElevatorMDOFModel(default_params)

    # Check diagonal elements are positive
    assert np.all(np.diag(model.M) > 0)
    # Check symmetry
    assert np.allclose(model.M, model.M.T)


def test_stiffness_matrix_assembly(default_params):
    """Test stiffness matrix assembly."""
    model = ElevatorMDOFModel(default_params)

    # Check diagonal elements are positive
    assert np.all(np.diag(model.K) > 0)
    # Check symmetry
    assert np.allclose(model.K, model.K.T)


def test_damping_matrix_assembly(default_params):
    """Test damping matrix assembly."""
    model = ElevatorMDOFModel(default_params)

    # Check diagonal elements are non-negative
    assert np.all(np.diag(model.C) >= 0)
    # Check symmetry
    assert np.allclose(model.C, model.C.T)


def test_state_space_matrices(default_params):
    """Test conversion to state-space form."""
    model = ElevatorMDOFModel(default_params)
    A, B = model.state_space_matrices()

    # Check dimensions
    assert A.shape == (12, 12)
    assert B.shape == (12, 1)

    # Check top-right block is identity (position-velocity coupling)
    assert np.allclose(A[:6, 6:], np.eye(6))

    # Check that bottom-left block has correct structure
    assert not np.allclose(A[6:, :6], np.zeros((6, 6)))


def test_natural_frequencies(default_params):
    """Test natural frequency computation."""
    model = ElevatorMDOFModel(default_params)
    freqs = model.compute_natural_frequencies()

    # Should return 3 frequencies
    assert len(freqs) == 3
    # All frequencies should be positive
    assert np.all(freqs > 0)
    # Should be in ascending order
    assert np.all(np.diff(freqs) >= 0)


def test_mass_matrix_invertible(default_params):
    """Test that mass matrix is invertible."""
    model = ElevatorMDOFModel(default_params)
    det_M = np.linalg.det(model.M)
    assert det_M != 0
    # Should be well-conditioned
    assert abs(det_M) > 1e-10


def test_parameter_sensitivity(default_params):
    """Test that model matrices change with parameter changes."""
    # Original model
    model1 = ElevatorMDOFModel(default_params)
    K1 = model1.K.copy()

    # Increase stiffness
    params_stiff = default_params.copy()
    params_stiff["k_isolation"] *= 1.5
    model2 = ElevatorMDOFModel(params_stiff)
    K2 = model2.K

    # Stiffness matrix should change
    assert not np.allclose(K1, K2)


def test_with_minimal_parameters():
    """Test model with minimal parameter set."""
    minimal_params = {
        "m_motor": 100,
        "m_traction": 1000,
        "m_car_frame": 1000,
        "m_cabin": 500,
        "m_counterweight": 2000,
        "k_rope_car": 1e5,
        "k_rope_counter": 1e5,
        "k_isolation": 1e5,
        "rope_stiffness": 1e10,
        "c_rope_car": 100,
        "c_rope_counter": 100,
        "c_isolation": 100,
        "damping": 50,
    }
    model = ElevatorMDOFModel(minimal_params)
    assert model.M is not None
    assert model.K is not None
    assert model.C is not None
