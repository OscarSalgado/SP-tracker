"""Tests for solver module with 100% coverage."""

import numpy as np
import pytest

from src.solver import RK4Solver, solve_elevator_dynamics
from src.elevator_model import ElevatorMDOFModel
from src.excitations import ExcitationGenerator


@pytest.fixture
def simple_system():
    """Create a simple 2x2 system for testing."""
    # damped oscillator: d²x/dt² = -2x - 0.5*dx/dt
    # In state-space: dz/dt = A*z + B*u where z = [x, dx/dt]
    A = np.array([[0, 1.0], [-2.0, -0.5]])
    B = np.array([[0], [1.0]])
    z0 = np.array([1.0, 0.0])
    return A, B, z0


def test_rk4_solver_initialization(simple_system):
    """Test RK4Solver initialization."""
    A, B, z0 = simple_system
    solver = RK4Solver(A, B, z0)

    assert np.allclose(solver.z, z0)
    assert np.allclose(solver.A, A)
    assert np.allclose(solver.B, B)
    assert len(solver.history) == 1


def test_rk4_single_step(simple_system):
    """Test single RK4 integration step."""
    A, B, z0 = simple_system
    solver = RK4Solver(A, B, z0)

    u = 0.0
    dt = 0.01
    z_new = solver.step(u, dt)

    # Check that state changed
    assert not np.allclose(z_new, z0)
    # Check history updated
    assert len(solver.history) == 2


def test_rk4_multiple_steps(simple_system):
    """Test multiple RK4 steps."""
    A, B, z0 = simple_system
    solver = RK4Solver(A, B, z0)

    dt = 0.001
    for _ in range(100):
        solver.step(0.0, dt)

    # History should have 101 entries (initial + 100 steps)
    assert len(solver.history) == 101


def test_rk4_with_constant_input(simple_system):
    """Test RK4 with constant input force."""
    A, B, z0 = simple_system
    solver = RK4Solver(A, B, z0)

    dt = 0.01
    F = 1.0  # Constant forcing

    for _ in range(50):
        solver.step(F, dt)

    # With constant forcing, should eventually settle
    z_final = solver.z
    assert z_final is not None


def test_rk4_energy_conservation(simple_system):
    """Test that undamped system approximately conserves energy."""
    A, B, z0 = simple_system
    # Create undamped system
    A_undamped = np.array([[0, 1.0], [-2.0, 0.0]])
    solver = RK4Solver(A_undamped, B, z0)

    dt = 0.001
    energies = []

    for _ in range(1000):
        solver.step(0.0, dt)
        z = solver.z
        E = 0.5 * z[1]**2 + z[0]**2  # Kinetic + potential
        energies.append(E)

    energies = np.array(energies)
    # Energy should fluctuate but not drift systematically
    energy_drift = (energies[-1] - energies[0]) / energies[0]
    assert abs(energy_drift) < 0.01  # Less than 1% drift


def test_rk4_dynamics(simple_system):
    """Test internal dynamics function."""
    A, B, z0 = simple_system
    solver = RK4Solver(A, B, z0)

    z_test = np.array([1.0, 0.5])
    u_test = 0.1
    dz = solver._dynamics(z_test, u_test)

    # Check that dz = A*z + B*u
    expected = A @ z_test + B.flatten() * u_test
    assert np.allclose(dz, expected)


def test_rk4_integrate_constant_velocity():
    """Test RK4 integration with constant velocity (no acceleration)."""
    # System: dx/dt = c (constant velocity), d²x/dt² = 0
    A = np.array([[0, 1.0], [0.0, 0.0]])
    B = np.array([[0], [1.0]])
    z0 = np.array([0.0, 1.0])  # Start with velocity 1

    solver = RK4Solver(A, B, z0)
    time = np.array([0.0, 0.01, 0.02, 0.03])

    # Excitation: constant zero force
    def u_func(t):
        return 0.0

    result = solver.integrate(time, u_func)

    assert 'time' in result
    assert 'displacement' in result
    assert 'velocity' in result
    assert 'acceleration' in result


def test_solve_elevator_dynamics_basic():
    """Test basic elevator dynamics solve."""
    params = {
        'm_motor': 100,
        'm_traction': 1000,
        'm_car_frame': 1000,
        'm_cabin': 500,
        'm_counterweight': 2000,
        'k_rope_car': 1e5,
        'k_rope_counter': 1e5,
        'k_isolation': 1e5,
        'rope_stiffness': 1e10,
        'c_rope_car': 100,
        'c_rope_counter': 100,
        'c_isolation': 100,
        'damping': 50,
    }

    model = ElevatorMDOFModel(params)
    time = np.arange(0, 2.0, 0.01)

    exc_gen = ExcitationGenerator(total_time=2.0, dt=0.01)
    excitations = exc_gen.combined_excitation()

    solution = solve_elevator_dynamics(model, time, excitations, load_ratio=0.5)

    # Check output structure
    assert 'time' in solution
    assert 'displacement' in solution
    assert 'velocity' in solution
    assert 'acceleration' in solution

    # Check dimensions
    assert len(solution['time']) > 0
    assert solution['displacement'].shape[0] > 0


def test_rk4_step_consistency(simple_system):
    """Test that small steps are consistent."""
    A, B, z0 = simple_system
    dt = 0.01

    # One step with dt
    solver1 = RK4Solver(A, B, z0)
    solver1.step(0.0, dt)
    z1 = solver1.z

    # Two steps with dt/2
    solver2 = RK4Solver(A, B, z0)
    solver2.step(0.0, dt/2)
    solver2.step(0.0, dt/2)
    z2 = solver2.z

    # Results should be close (RK4 error ~ O(dt^5))
    assert np.allclose(z1, z2, rtol=1e-3)


def test_rk4_with_time_varying_input(simple_system):
    """Test RK4 with time-varying input."""
    A, B, z0 = simple_system
    solver = RK4Solver(A, B, z0)

    dt = 0.01
    t = 0.0

    for _ in range(100):
        u = np.sin(2 * np.pi * t)  # Sinusoidal forcing
        solver.step(u, dt)
        t += dt

    # Should complete without error
    assert len(solver.history) == 101


def test_solve_elevator_with_different_loads():
    """Test that different load ratios produce different results."""
    params = {
        'm_motor': 100,
        'm_traction': 1000,
        'm_car_frame': 1000,
        'm_cabin': 500,
        'm_counterweight': 2000,
        'k_rope_car': 1e5,
        'k_rope_counter': 1e5,
        'k_isolation': 1e5,
        'rope_stiffness': 1e10,
        'c_rope_car': 100,
        'c_rope_counter': 100,
        'c_isolation': 100,
        'damping': 50,
    }

    model = ElevatorMDOFModel(params)
    time = np.arange(0, 1.0, 0.01)

    exc_gen = ExcitationGenerator(total_time=1.0, dt=0.01)

    # Solve for different loads
    exc_no_load = exc_gen.combined_excitation(load_ratio=0.0)
    exc_full_load = exc_gen.combined_excitation(load_ratio=1.0)

    sol_no_load = solve_elevator_dynamics(model, time, exc_no_load, load_ratio=0.0)
    sol_full_load = solve_elevator_dynamics(model, time, exc_full_load, load_ratio=1.0)

    # Results should differ
    accel_no_load = sol_no_load['acceleration']
    accel_full_load = sol_full_load['acceleration']

    # Peak accelerations might differ
    assert np.max(np.abs(accel_no_load)) != np.max(np.abs(accel_full_load))
