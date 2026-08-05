"""Whitening-Based Deconvolution (WBD) para eliminar función de transferencia."""

import numpy as np


class WhiteningBasedDeconvolution:
    """Método WBD para deconvolución basada en blanqueamiento.

    Elimina el efecto de la función de transferencia del sistema de manera ciega,
    sin requerir estimación explícita de la función de transferencia.
    """

    def __init__(self, fft_size: int = 1024, num_iterations: int = 10):
        """
        Args:
            fft_size: Tamaño de FFT para procesamiento espectral.
            num_iterations: Número de iteraciones del algoritmo.
        """
        self.fft_size = fft_size
        self.num_iterations = num_iterations

    def whiten_spectrum(self, signal_data: np.ndarray) -> np.ndarray:
        """Blanquea el espectro normalizando magnitudes.

        Args:
            signal_data: Señal de entrada (array 1D).

        Returns:
            Señal blanqueada en dominio temporal.
        """
        fft_signal = np.fft.fft(signal_data, n=self.fft_size)
        magnitude = np.abs(fft_signal)
        phase = np.angle(fft_signal)

        magnitude_min = np.min(magnitude[magnitude > 0])
        magnitude = np.maximum(magnitude, magnitude_min)

        whitened_mag = magnitude / (np.abs(magnitude) + 1e-10)

        whitened_fft = whitened_mag * np.exp(1j * phase)
        whitened_signal = np.fft.ifft(whitened_fft, n=self.fft_size).real

        return whitened_signal[: len(signal_data)]

    def deconvolve(self, observed_signal: np.ndarray) -> np.ndarray:
        """Realiza deconvolución ciega mediante iteraciones de blanqueamiento.

        Args:
            observed_signal: Señal observada (distorsionada por función transferencia).

        Returns:
            Señal deconvolucionada estimada.
        """
        current = np.copy(observed_signal)

        for _ in range(self.num_iterations):
            whitened = self.whiten_spectrum(current)
            current = whitened

        return current

    def estimate_transfer_function(self, signal_data: np.ndarray) -> np.ndarray:
        """Estima la función de transferencia a partir de cambios espectrales.

        Args:
            signal_data: Señal de entrada.

        Returns:
            Función de transferencia estimada (en dominio frecuencial).
        """
        original_fft = np.fft.fft(signal_data, n=self.fft_size)
        original_mag = np.abs(original_fft)

        whitened_signal = self.whiten_spectrum(signal_data)
        whitened_fft = np.fft.fft(whitened_signal, n=self.fft_size)
        whitened_mag = np.abs(whitened_fft)

        with np.errstate(divide="ignore", invalid="ignore"):
            transfer_func = original_mag / (whitened_mag + 1e-10)
            transfer_func = np.nan_to_num(transfer_func, nan=1.0, posinf=1.0)

        return transfer_func
