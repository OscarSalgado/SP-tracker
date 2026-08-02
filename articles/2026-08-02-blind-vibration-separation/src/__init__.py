"""Blind separation of vibration components using STFT-based algorithms.

Based on "Blind separation of vibration components: Principles and demonstrations"
by Jérôme Antoni (2005).
"""

import numpy as np
from scipy import signal


def extract_periodic_components(
    x: np.ndarray,
    fs: float,
    nperseg: int = 512,
    noverlap: int = None,
    window: str = "hann",
) -> np.ndarray:
    """Extract periodic components using spectral filtering.

    Identifies and extracts frequency bins with high energy and low variability
    (characteristic of periodic signals) versus random signals.

    Args:
        x: Input vibration signal (1D array).
        fs: Sampling frequency (Hz).
        nperseg: Length of each STFT segment.
        noverlap: Number of overlapping samples (default: nperseg//2).
        window: Window function for STFT.

    Returns:
        Periodic component (1D array, same length as x).
    """
    if noverlap is None:
        noverlap = nperseg // 2

    f, t, Zxx = signal.stft(x, fs=fs, nperseg=nperseg, noverlap=noverlap, window=window)

    power = np.abs(Zxx) ** 2
    mean_power = np.mean(power, axis=1)
    std_power = np.std(power, axis=1)

    snr_per_freq = mean_power / (std_power + 1e-10)
    snr_threshold = np.percentile(snr_per_freq, 50)

    mask = (snr_per_freq > snr_threshold).astype(float)

    Zxx_periodic = Zxx * mask[:, np.newaxis]

    periodic = signal.istft(Zxx_periodic, fs=fs, nperseg=nperseg, window=window)[1]
    return periodic[: len(x)]


def spectral_kurtosis(
    x: np.ndarray,
    fs: float,
    nperseg: int = 512,
    noverlap: int = None,
    window: str = "hann",
) -> tuple[np.ndarray, np.ndarray]:
    """Compute spectral kurtosis to identify impulsive (non-stationary) content.

    Spectral kurtosis measures deviation from Gaussianity: zero for stationary
    Gaussian signals, positive for impulsive/transient signals.

    Args:
        x: Input signal (1D array).
        fs: Sampling frequency (Hz).
        nperseg: Length of each STFT segment.
        noverlap: Number of overlapping samples.
        window: Window function.

    Returns:
        Tuple of (frequencies, spectral_kurtosis).
    """
    if noverlap is None:
        noverlap = nperseg // 2

    f, t, Zxx = signal.stft(x, fs=fs, nperseg=nperseg, noverlap=noverlap, window=window)

    mag = np.abs(Zxx)

    S2 = np.mean(mag**2, axis=1)
    S4 = np.mean(mag**4, axis=1)

    K = (S4 / (S2**2 + 1e-10)) - 2

    return f, K


def extract_transient_components(
    x: np.ndarray,
    fs: float,
    nperseg: int = 512,
    noverlap: int = None,
    window: str = "hann",
) -> np.ndarray:
    """Extract transient (non-stationary/impulsive) components using spectral kurtosis.

    Uses high spectral kurtosis as a marker of impulsive content and extracts
    frequency bands with elevated kurtosis.

    Args:
        x: Input signal (1D array).
        fs: Sampling frequency (Hz).
        nperseg: Length of each STFT segment.
        noverlap: Number of overlapping samples.
        window: Window function.

    Returns:
        Transient component (1D array, same length as x).
    """
    if noverlap is None:
        noverlap = nperseg // 2

    f, K = spectral_kurtosis(x, fs, nperseg, noverlap, window)

    K_clipped = np.maximum(K, 0)
    max_K = np.max(K_clipped) + 1e-10
    W = np.sqrt(K_clipped / max_K)

    f_stft, t, Zxx = signal.stft(x, fs=fs, nperseg=nperseg, noverlap=noverlap, window=window)

    Zxx_filtered = Zxx * W[:, np.newaxis]

    transient = signal.istft(Zxx_filtered, fs=fs, nperseg=nperseg, window=window)[1]
    return transient[: len(x)]


def separate_vibration_signal(
    x: np.ndarray,
    fs: float,
    nperseg: int = 512,
    noverlap: int = None,
    window: str = "hann",
) -> dict[str, np.ndarray]:
    """Decompose a vibration signal into periodic, transient, and residual components.

    Follows the deflation approach: first extract periodic (deterministic) components,
    then from the residual extract transient (impulsive) components.

    Args:
        x: Input vibration signal (1D array).
        fs: Sampling frequency (Hz).
        nperseg: STFT segment length.
        noverlap: STFT overlap in samples.
        window: Window function.

    Returns:
        Dictionary with keys:
        - 'periodic': periodic component
        - 'random_residual': random part after periodic extraction
        - 'transient': transient/non-stationary component
        - 'stationary_residual': final stationary noise component
    """
    periodic = extract_periodic_components(x, fs, nperseg, noverlap, window)
    random_residual = x - periodic

    transient = extract_transient_components(random_residual, fs, nperseg, noverlap, window)
    stationary_residual = random_residual - transient

    return {
        "periodic": periodic,
        "random_residual": random_residual,
        "transient": transient,
        "stationary_residual": stationary_residual,
    }
