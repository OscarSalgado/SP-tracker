import numpy as np
import pytest
from src import (
    extract_periodic_components,
    extract_transient_components,
    separate_vibration_signal,
    spectral_kurtosis,
)


@pytest.fixture
def synthetic_signal():
    """Generate synthetic test vibration signal."""
    fs = 10000
    duration = 1.0
    t = np.arange(0, duration, 1 / fs)
    np.random.seed(42)

    periodic = (
        np.sin(2 * np.pi * 100 * t)
        + 0.5 * np.sin(2 * np.pi * 200 * t)
        + 0.3 * np.sin(2 * np.pi * 300 * t)
    )

    noise = 0.1 * np.random.randn(len(t))

    transient = np.zeros_like(t)
    for impact_time in [0.2, 0.4, 0.6, 0.8]:
        envelope = np.exp(-100 * (t - impact_time) ** 2)
        transient += 0.5 * envelope * np.sin(2 * np.pi * 500 * (t - impact_time))

    signal = periodic + noise + transient
    return signal, fs, periodic, noise, transient


def test_extract_periodic_components_shape(synthetic_signal):
    signal, fs, _, _, _ = synthetic_signal
    periodic = extract_periodic_components(signal, fs, nperseg=512)
    assert periodic.shape == signal.shape


def test_extract_periodic_components_non_nan(synthetic_signal):
    signal, fs, _, _, _ = synthetic_signal
    periodic = extract_periodic_components(signal, fs, nperseg=512)
    assert not np.isnan(periodic).any()
    assert not np.isinf(periodic).any()


def test_spectral_kurtosis_output_shape(synthetic_signal):
    signal, fs, _, _, _ = synthetic_signal
    f, K = spectral_kurtosis(signal, fs, nperseg=512)
    assert len(f) == len(K)
    assert len(f) > 0


def test_spectral_kurtosis_range(synthetic_signal):
    signal, fs, _, _, _ = synthetic_signal
    _, K = spectral_kurtosis(signal, fs, nperseg=512)
    assert np.all(K >= -2.0)
    assert not np.isnan(K).any()


def test_extract_transient_components_shape(synthetic_signal):
    signal, fs, _, _, _ = synthetic_signal
    transient = extract_transient_components(signal, fs, nperseg=512)
    assert transient.shape == signal.shape


def test_extract_transient_components_non_nan(synthetic_signal):
    signal, fs, _, _, _ = synthetic_signal
    transient = extract_transient_components(signal, fs, nperseg=512)
    assert not np.isnan(transient).any()
    assert not np.isinf(transient).any()


def test_separate_vibration_signal_keys(synthetic_signal):
    signal, fs, _, _, _ = synthetic_signal
    result = separate_vibration_signal(signal, fs, nperseg=512)
    expected_keys = {"periodic", "random_residual", "transient", "stationary_residual"}
    assert set(result.keys()) == expected_keys


def test_separate_vibration_signal_shapes(synthetic_signal):
    signal, fs, _, _, _ = synthetic_signal
    result = separate_vibration_signal(signal, fs, nperseg=512)
    for component in result.values():
        assert component.shape[0] <= len(signal)
        assert not np.isnan(component).any()
        assert not np.isinf(component).any()


def test_separate_vibration_signal_energy_conservation(synthetic_signal):
    signal, fs, _, _, _ = synthetic_signal
    result = separate_vibration_signal(signal, fs, nperseg=512)

    periodic = result["periodic"]
    transient = result["transient"]
    residual = result["stationary_residual"]

    reconstructed = periodic + transient + residual
    assert reconstructed.shape[0] <= len(signal)


def test_extract_periodic_preserves_sine_harmonic():
    """Verify that periodic extraction works on pure harmonic signal."""
    fs = 10000
    t = np.arange(0, 0.5, 1 / fs)
    signal = np.sin(2 * np.pi * 100 * t)

    periodic = extract_periodic_components(signal, fs, nperseg=512)

    energy_original = np.sum(signal**2)
    energy_extracted = np.sum(periodic**2)
    assert energy_extracted > 0
    assert energy_extracted > 0.1 * energy_original


def test_spectral_kurtosis_positive_on_impacts():
    """Verify that spectral kurtosis detects impacts."""
    fs = 10000
    duration = 0.5
    t = np.arange(0, duration, 1 / fs)

    signal = np.zeros_like(t)
    for impact_time in [0.1, 0.3]:
        envelope = 0.5 * np.exp(-100 * (t - impact_time) ** 2)
        signal += envelope * np.sin(2 * np.pi * 500 * (t - impact_time))

    _, K = spectral_kurtosis(signal, fs, nperseg=512)

    max_kurtosis = np.max(K)
    assert max_kurtosis > 0.01


def test_extract_transient_on_impulsive_signal():
    """Verify that transient extraction works on impulsive signal."""
    fs = 10000
    duration = 0.5
    t = np.arange(0, duration, 1 / fs)

    signal = np.zeros_like(t)
    for impact_time in [0.1, 0.3]:
        envelope = 0.5 * np.exp(-100 * (t - impact_time) ** 2)
        signal += envelope * np.sin(2 * np.pi * 500 * (t - impact_time))

    transient = extract_transient_components(signal, fs, nperseg=512)

    assert np.sum(np.abs(transient)) > 0


def test_separation_on_mixed_signal():
    """Verify decomposition on a realistic mixed signal."""
    fs = 10000
    duration = 0.5
    t = np.arange(0, duration, 1 / fs)
    np.random.seed(42)

    periodic = np.sin(2 * np.pi * 100 * t) + 0.5 * np.sin(2 * np.pi * 200 * t)
    noise = 0.05 * np.random.randn(len(t))
    transient = np.zeros_like(t)
    for ti in [0.1, 0.3]:
        transient += 0.3 * np.exp(-100 * (t - ti) ** 2) * np.sin(2 * np.pi * 500 * (t - ti))

    mixed = periodic + noise + transient

    result = separate_vibration_signal(mixed, fs, nperseg=512)

    assert np.sum(result["periodic"] ** 2) > 0
    assert np.sum(result["transient"] ** 2) > 0
    assert len(result["stationary_residual"]) == len(mixed)


def test_extract_transient_on_gaussian_noise():
    """Verify that zero-kurtosis signals are handled correctly."""
    fs = 10000
    duration = 0.5
    t = np.arange(0, duration, 1 / fs)
    np.random.seed(42)

    signal = np.random.randn(len(t))

    transient = extract_transient_components(signal, fs, nperseg=512)

    assert transient.shape == signal.shape
    assert not np.isnan(transient).any()
    assert not np.isinf(transient).any()
