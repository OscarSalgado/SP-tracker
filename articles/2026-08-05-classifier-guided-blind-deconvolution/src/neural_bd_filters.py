"""Filtros neurales para deconvolución ciega en dominio temporal y frecuencial."""

import numpy as np
import torch
import torch.nn as nn


class TemporalFilter(nn.Module):
    """Filtro temporal aprendible para deconvolución."""

    def __init__(self, filter_length: int = 64):
        """
        Args:
            filter_length: Longitud del filtro temporal.
        """
        super().__init__()
        self.filter_length = filter_length
        self.filter = nn.Parameter(torch.randn(1, 1, filter_length) * 0.1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Convoluciona con el filtro temporal aprendible."""
        return torch.nn.functional.conv1d(x, self.filter, padding=self.filter_length // 2)


class FrequencyFilter(nn.Module):
    """Filtro frecuencial (red neuronal FC) para deconvolución."""

    def __init__(self, fft_size: int = 256):
        """
        Args:
            fft_size: Tamaño de FFT.
        """
        super().__init__()
        self.fft_size = fft_size

        self.fc = nn.Sequential(
            nn.Linear(fft_size // 2, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, fft_size // 2),
        )

    def forward(self, freq_magnitude: np.ndarray) -> np.ndarray:
        """Amplifica magnitudes en dominio frecuencial.

        Args:
            freq_magnitude: Magnitud espectral (array numpy).

        Returns:
            Magnitud espectral amplificada.
        """
        x = torch.tensor(freq_magnitude, dtype=torch.float32).unsqueeze(0)
        with torch.no_grad():
            out = self.fc(x)
        return out.squeeze().numpy()


class NeuralBlindDeconvolution:
    """Deconvolución ciega basada en filtros neurales."""

    def __init__(self, temporal_length: int = 64, fft_size: int = 256):
        """
        Args:
            temporal_length: Longitud del filtro temporal.
            fft_size: Tamaño de FFT para procesamiento frecuencial.
        """
        self.temporal_filter = TemporalFilter(temporal_length)
        self.frequency_filter = FrequencyFilter(fft_size)
        self.fft_size = fft_size

    def deconvolve(self, signal: np.ndarray) -> np.ndarray:
        """Aplica deconvolución ciega neural."""
        signal_tensor = torch.tensor(signal, dtype=torch.float32).unsqueeze(0).unsqueeze(0)

        with torch.no_grad():
            temporal_filtered = self.temporal_filter(signal_tensor)

        temporal_result = temporal_filtered.squeeze().numpy()

        fft_vals = np.fft.fft(temporal_result, n=self.fft_size)
        magnitude = np.abs(fft_vals[: self.fft_size // 2])

        self.frequency_filter.forward(magnitude)

        return temporal_result[: len(signal)]
