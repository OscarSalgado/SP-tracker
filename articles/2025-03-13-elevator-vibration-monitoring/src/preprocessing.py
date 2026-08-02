"""Preprocesamiento de señales de vibración con transformada wavelet continua."""

import numpy as np
import torch
from scipy import signal


class CWTTransform:
    """Transforma señales 1D de aceleración a espectrogramas 2D con CWT."""

    def __init__(
        self,
        frequencies: tuple[float, float] = (0, 100),
        num_scales: int = 32,
        wavelet: str = "morl",
    ):
        """Inicializa el transformador CWT.

        Args:
            frequencies: Rango de frecuencias (Hz) a considerar.
            num_scales: Número de escalas (resolución de frecuencia).
            wavelet: Tipo de wavelet (morl=Morlet, mexh=Sombrero mexicano).
        """
        self.frequencies = frequencies
        self.num_scales = num_scales
        self.wavelet = wavelet

    def __call__(self, signal_data: np.ndarray) -> np.ndarray:
        """Aplica CWT a una señal 1D.

        Args:
            signal_data: Señal 1D de forma (time_steps,).

        Returns:
            Espectrograma 2D de forma (scales, time_steps).
        """
        scales = np.linspace(1, self.num_scales, self.num_scales)
        coefficients = signal.cwt(signal_data, signal.morlet2, scales)
        return np.abs(coefficients)

    def normalize(self, spectrogram: np.ndarray) -> np.ndarray:
        """Normaliza el espectrograma a rango [0, 1]."""
        spec_min = np.min(spectrogram)
        spec_max = np.max(spectrogram)
        if spec_max - spec_min > 1e-6:
            return (spectrogram - spec_min) / (spec_max - spec_min)
        return spectrogram


class ElevatorDataPreprocessor:
    """Preprocesa datos brutos de aceleración de ascensores."""

    def __init__(
        self,
        sampling_rate: int = 12000,
        window_size: int = 4096,
        overlap: float = 0.5,
    ):
        """Inicializa el preprocesador.

        Args:
            sampling_rate: Frecuencia de muestreo (Hz).
            window_size: Tamaño de ventana para segmentación.
            overlap: Fracción de superposición entre ventanas (0-1).
        """
        self.sampling_rate = sampling_rate
        self.window_size = window_size
        self.overlap = overlap
        self.cwt = CWTTransform()

    def segment_signal(self, signal_data: np.ndarray) -> list[np.ndarray]:
        """Divide una señal en ventanas con superposición.

        Args:
            signal_data: Señal 1D de forma (total_samples,).

        Returns:
            Lista de ventanas segmentadas.
        """
        stride = int(self.window_size * (1 - self.overlap))
        segments = []
        for i in range(0, len(signal_data) - self.window_size, stride):
            segments.append(signal_data[i : i + self.window_size])
        return segments

    def process(self, signal_data: np.ndarray) -> torch.Tensor:
        """Procesa una señal bruta a tensor de espectrogramas.

        Args:
            signal_data: Señal 1D de aceleración.

        Returns:
            Tensor de forma (num_segments, height, width) con espectrogramas.
        """
        segments = self.segment_signal(signal_data)
        spectrograms = []

        for segment in segments:
            spec = self.cwt(segment)
            spec = self.cwt.normalize(spec)
            spectrograms.append(spec)

        return torch.tensor(spectrograms, dtype=torch.float32)

    @staticmethod
    def create_rgb_image(spectrogram: np.ndarray) -> np.ndarray:
        """Convierte espectrograma a imagen RGB para entrada de red.

        Args:
            spectrogram: Espectrograma 2D normalizado.

        Returns:
            Imagen RGB de forma (3, height, width).
        """
        if spectrogram.ndim != 2:
            raise ValueError(f"Expected 2D spectrogram, got shape {spectrogram.shape}")

        height, width = spectrogram.shape
        rgb_image = np.zeros((3, height, width), dtype=np.float32)

        rgb_image[0] = spectrogram
        rgb_image[1] = spectrogram
        rgb_image[2] = spectrogram

        return rgb_image
