"""Pipeline integrada para separación ciega de vibración."""

import numpy as np
import torch
from scipy import signal as sp_signal
from scipy.interpolate import interp1d

from .dilated_cnn import DilatedCNN
from .whitening_deconvolution import WhiteningBasedDeconvolution


class VibrationSeparator:
    """Pipeline para separar ciegos de vibración de engranajes y rodamientos.

    Implementa el método de dos etapas:
    1. CNN dilated para aislamiento de engranaje.
    2. Deconvolución sobre residuo para rodamiento.
    """

    def __init__(self, fft_size: int = 1024, num_cnn_layers: int = 4):
        """
        Args:
            fft_size: Tamaño de FFT para procesamiento espectral.
            num_cnn_layers: Número de capas de la CNN dilated.
        """
        self.fft_size = fft_size
        self.cnn = DilatedCNN(num_layers=num_cnn_layers)
        self.wbd = WhiteningBasedDeconvolution(fft_size=fft_size)

    def compute_envelope(self, signal_data: np.ndarray) -> np.ndarray:
        """Calcula la envolvente analítica (demodulación)."""
        analytic_signal = sp_signal.hilbert(signal_data)
        envelope = np.abs(analytic_signal)
        return envelope

    def compute_log_envelope(self, signal_data: np.ndarray, eps: float = 1e-10) -> np.ndarray:
        """Calcula log-envolvente (para rodamientos)."""
        envelope = self.compute_envelope(signal_data)
        return np.log(envelope + eps) ** 2

    def separate_sources(self, mixed_signal: np.ndarray, use_cnn_for_gear: bool = True) -> dict:
        """Separa ciegamente vibraciones de engranaje y rodamiento.

        Args:
            mixed_signal: Señal mezclada observada.
            use_cnn_for_gear: Si True, usa CNN para engranaje. Si False, usa envolvente.

        Returns:
            Dict con claves:
            - 'gear': Vibración de engranaje estimada.
            - 'bearing': Vibración de rodamiento estimada.
            - 'residue': Residuo después de separación.
        """
        mixed_signal = np.asarray(mixed_signal, dtype=np.float32)
        original_len = len(mixed_signal)

        if use_cnn_for_gear:
            x = torch.tensor([mixed_signal], dtype=torch.float32).unsqueeze(1)
            with torch.no_grad():
                gear_output = self.cnn(x).squeeze().numpy()
            gear_indices = np.arange(len(gear_output))
            target_indices = np.linspace(0, len(gear_output) - 1, original_len)
            f_interp = interp1d(gear_indices, gear_output, kind="linear", fill_value="extrapolate")
            gear_estimated = f_interp(target_indices)
        else:
            gear_estimated = self.compute_envelope(mixed_signal)

        gear_estimated = np.clip(gear_estimated, 0, np.max(np.abs(mixed_signal)))

        residue = mixed_signal - gear_estimated

        bearing_log_env = self.compute_log_envelope(residue)

        bearing_deconvolved = self.wbd.deconvolve(bearing_log_env)
        if len(bearing_deconvolved) != original_len:
            bearing_indices = np.arange(len(bearing_deconvolved))
            target_bear_indices = np.linspace(0, len(bearing_deconvolved) - 1, original_len)
            f_bearing = interp1d(
                bearing_indices, bearing_deconvolved, kind="linear", fill_value="extrapolate"
            )
            bearing_deconvolved = f_bearing(target_bear_indices)

        return {
            "gear": gear_estimated,
            "bearing": bearing_deconvolved,
            "residue": residue,
        }

    def get_cnn(self) -> DilatedCNN:
        """Retorna el modelo CNN para entrenamiento personalizado."""
        return self.cnn

    def get_deconvolution_model(self) -> WhiteningBasedDeconvolution:
        """Retorna el modelo WBD para ajuste personalizado."""
        return self.wbd
