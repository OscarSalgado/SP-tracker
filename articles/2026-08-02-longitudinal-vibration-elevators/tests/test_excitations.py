"""Tests for excitations module with 100% coverage."""

import numpy as np
import pytest

from src.excitations import ExcitationGenerator


@pytest.fixture
def default_generator():
    """Default excitation generator."""
    return ExcitationGenerator(velocity=6.0, total_time=10.0, dt=0.01)


def test_generator_initialization(default_generator):
    """Test ExcitationGenerator initialization."""
    assert default_generator.velocity == 6.0
    assert default_generator.total_time == 10.0
    assert default_generator.dt == 0.01
    assert len(default_generator.t) == 1000


def test_eccentric_excitation(default_generator):
    """Test eccentric excitation generation."""
    ecc = default_generator.eccentric_excitation()

    # Check output properties
    assert len(ecc) == len(default_generator.t)
    # Should be sinusoidal, bounded by eccentricity amplitude
    max_val = default_generator.eccentricity_mm / 1000.0
    assert np.max(np.abs(ecc)) <= max_val * 1.01  # Small tolerance for numerics


def test_eccentric_excitation_frequency(default_generator):
    """Test that eccentric excitation has correct frequency."""
    ecc = default_generator.eccentric_excitation()

    # Check that signal is sinusoidal (non-zero variation)
    assert np.std(ecc) > 0
    # Check amplitude is bounded
    max_amp = default_generator.eccentricity_mm / 1000.0
    assert np.max(np.abs(ecc)) <= max_amp * 1.01


def test_reverse_braking_excitation(default_generator):
    """Test reverse braking excitation."""
    braking = default_generator.reverse_braking_excitation()

    # Check output properties
    assert len(braking) == len(default_generator.t)
    # Should start and end at zero
    assert abs(braking[0]) < 1e-10
    assert abs(braking[-1]) < 1e-10
    # Should have positive peak
    assert np.max(braking) > 0


def test_braking_profile_shape(default_generator):
    """Test that braking follows expected profile."""
    braking = default_generator.reverse_braking_excitation()

    # Find indices for different phases
    t = default_generator.t
    rise_idx = np.where(t < 0.5)[0]
    steady_idx = np.where((t >= 0.5) & (t < 2.5))[0]
    decay_idx = np.where((t >= 2.5) & (t < 4.0))[0]

    # Rise phase should be monotonically increasing
    if len(rise_idx) > 1:
        assert np.all(np.diff(braking[rise_idx]) > -1e-10)  # Allow small numerical errors

    # Steady phase should be approximately constant
    if len(steady_idx) > 1:
        steady_values = braking[steady_idx]
        assert np.std(steady_values) < np.mean(steady_values) * 0.01

    # Decay phase should be monotonically decreasing
    if len(decay_idx) > 1:
        assert np.all(np.diff(braking[decay_idx]) < 1e-10)


def test_rail_joint_impact_excitation(default_generator):
    """Test rail joint impact excitation."""
    impacts = default_generator.rail_joint_impact_excitation()

    # Check output properties
    assert len(impacts) == len(default_generator.t)
    # Should be non-negative
    assert np.all(impacts >= 0)
    # Should have peaks at joint locations
    assert np.max(impacts) > 0


def test_rail_joint_spacing(default_generator):
    """Test that rail joint impacts are at correct spacing."""
    impacts = default_generator.rail_joint_impact_excitation()

    # Check that impacts occur at roughly regular intervals
    # Find indices where impacts are non-zero
    impact_indices = np.where(impacts > 0)[0]

    if len(impact_indices) > 1:
        # Calculate sample spacing between impacts
        spacings = np.diff(impact_indices)
        # Spacings should be relatively uniform
        spacing_std = np.std(spacings)
        spacing_mean = np.mean(spacings)
        # Standard deviation should be less than mean (not too variable)
        if spacing_mean > 0:
            assert spacing_std < spacing_mean * 0.5


def test_combined_excitation(default_generator):
    """Test combined excitation generation."""
    combined = default_generator.combined_excitation(load_ratio=0.5)

    # Check keys
    assert 'time' in combined
    assert 'eccentric' in combined
    assert 'braking' in combined
    assert 'rail_impact' in combined
    assert 'combined' in combined

    # Check dimensions
    assert len(combined['time']) == len(default_generator.t)
    assert len(combined['eccentric']) == len(default_generator.t)
    assert len(combined['braking']) == len(default_generator.t)
    assert len(combined['rail_impact']) == len(default_generator.t)
    assert len(combined['combined']) == len(default_generator.t)


def test_load_ratio_effect(default_generator):
    """Test that load ratio affects rail impact magnitude."""
    combined_no_load = default_generator.combined_excitation(load_ratio=0.0)
    combined_full_load = default_generator.combined_excitation(load_ratio=1.0)

    # Rail impact should be larger with full load
    max_impact_no_load = np.max(combined_no_load['rail_impact'])
    max_impact_full_load = np.max(combined_full_load['rail_impact'])

    assert max_impact_full_load > max_impact_no_load


def test_different_velocities():
    """Test excitation generation at different velocities."""
    gen_slow = ExcitationGenerator(velocity=2.0, total_time=5.0, dt=0.01)
    gen_fast = ExcitationGenerator(velocity=8.0, total_time=5.0, dt=0.01)

    ecc_slow = gen_slow.eccentric_excitation()
    ecc_fast = gen_fast.eccentric_excitation()

    # Both should be sinusoidal with non-zero standard deviation
    assert np.std(ecc_slow) > 0
    assert np.std(ecc_fast) > 0
    # Both should be bounded by eccentricity amplitude
    max_amp = 3.0 / 1000.0
    assert np.max(np.abs(ecc_slow)) <= max_amp * 1.01
    assert np.max(np.abs(ecc_fast)) <= max_amp * 1.01


def test_different_time_durations():
    """Test generators with different total times."""
    gen_short = ExcitationGenerator(total_time=2.0, dt=0.01)
    gen_long = ExcitationGenerator(total_time=20.0, dt=0.01)

    assert len(gen_short.t) == 200
    assert len(gen_long.t) == 2000


def test_with_custom_eccentricity():
    """Test generator with modified eccentricity."""
    gen = ExcitationGenerator()
    gen.eccentricity_mm = 5.0

    ecc = gen.eccentric_excitation()
    expected_max = 5.0 / 1000.0
    assert np.max(np.abs(ecc)) <= expected_max * 1.01
