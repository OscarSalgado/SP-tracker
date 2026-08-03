"""Tests for generate_synthetic_data module."""

import numpy as np
from src.generate_synthetic_data import (
    generate_scenario,
    get_default_parameters,
    main,
)


def test_get_default_parameters():
    """Test default parameters dictionary."""
    params = get_default_parameters()

    # Check all required keys exist
    required_keys = {
        "m_motor",
        "m_traction",
        "m_car_frame",
        "m_cabin",
        "m_counterweight",
        "k_rope_car",
        "k_rope_counter",
        "k_isolation",
        "rope_stiffness",
        "c_rope_car",
        "c_rope_counter",
        "c_isolation",
        "damping",
    }
    assert required_keys.issubset(params.keys())

    # Check all values are positive
    assert all(v > 0 for v in params.values())


def test_generate_scenario_no_load():
    """Test scenario generation with no load."""
    result = generate_scenario("no_load", 0.0, velocity=6.0, duration=2.0, dt=0.1)

    assert result["scenario"] == "no_load"
    assert result["load_ratio"] == 0.0
    assert "time" in result
    assert "car_acceleration" in result
    assert "rope_stress" in result
    assert "excitations" in result
    assert "natural_frequencies" in result

    # Check data shapes
    expected_len = int(2.0 / 0.1)
    assert len(result["time"]) == expected_len
    assert len(result["car_acceleration"]) == expected_len
    assert len(result["rope_stress"]) == expected_len


def test_generate_scenario_half_load():
    """Test scenario generation with half load."""
    result = generate_scenario("half_load", 0.5, duration=2.0, dt=0.1)

    assert result["load_ratio"] == 0.5
    assert np.max(result["rope_stress"]) > 0
    assert np.min(result["rope_stress"]) >= 0


def test_generate_scenario_full_load():
    """Test scenario generation with full load."""
    result = generate_scenario("full_load", 1.0, duration=2.0, dt=0.1)

    assert result["load_ratio"] == 1.0
    # Rope stress should be higher with full load
    assert np.max(result["rope_stress"]) > 400  # Should be significantly above baseline


def test_scenario_load_effect():
    """Test that load ratio affects results appropriately."""
    result_no_load = generate_scenario("no_load", 0.0, duration=1.0, dt=0.05)
    result_full_load = generate_scenario("full_load", 1.0, duration=1.0, dt=0.05)

    # Rope stress should increase with load
    stress_no = np.mean(result_no_load["rope_stress"])
    stress_full = np.mean(result_full_load["rope_stress"])
    assert stress_full > stress_no


def test_scenario_excitations_included():
    """Test that excitation components are included."""
    result = generate_scenario("test", 0.5, duration=1.0, dt=0.1)

    exc = result["excitations"]
    assert "eccentric" in exc
    assert "braking" in exc
    assert "rail_impact" in exc

    # Check that excitations have correct length
    expected_len = 10
    assert len(exc["eccentric"]) == expected_len
    assert len(exc["braking"]) == expected_len
    assert len(exc["rail_impact"]) == expected_len


def test_scenario_natural_frequencies():
    """Test that natural frequencies are computed."""
    result = generate_scenario("test", 0.5, duration=1.0, dt=0.1)

    freqs = result["natural_frequencies"]
    assert len(freqs) == 3
    assert all(f > 0 for f in freqs)


def test_scenario_different_velocities():
    """Test scenarios at different velocities."""
    result_slow = generate_scenario("slow", 0.5, velocity=2.0, duration=1.0, dt=0.05)
    result_fast = generate_scenario("fast", 0.5, velocity=8.0, duration=1.0, dt=0.05)

    # Both should complete successfully
    assert len(result_slow["car_acceleration"]) > 0
    assert len(result_fast["car_acceleration"]) > 0


def test_scenario_stress_bounds():
    """Test that rope stress remains within physical bounds."""
    result = generate_scenario("test", 1.0, duration=2.0, dt=0.1)

    stress = result["rope_stress"]
    # Rope stress should not exceed material limits
    assert np.max(stress) <= 750  # Wire rope yield stress


def test_scenario_acceleration_reasonable():
    """Test that acceleration values are physically reasonable."""
    result = generate_scenario("test", 0.5, duration=2.0, dt=0.1)

    accel = result["car_acceleration"]
    # Elevator acceleration should be less than 1 g
    assert np.max(np.abs(accel)) < 9.81


def test_main_function():
    """Test the main() function that generates and saves data."""
    # Run main function
    result = main()

    # Check that result is a dictionary with scenarios
    assert isinstance(result, dict)
    assert "no_load" in result
    assert "half_load" in result
    assert "full_load" in result

    # Check that each scenario has required keys
    for scenario in result.values():
        assert "time" in scenario
        assert "car_acceleration" in scenario
        assert "rope_stress" in scenario
        assert "natural_frequencies" in scenario
        assert "excitations" in scenario
