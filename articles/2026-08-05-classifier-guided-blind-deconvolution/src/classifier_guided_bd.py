"""Pipeline ClassBD: deconvolución ciega guiada por clasificador."""

import numpy as np
import torch
import torch.nn as nn

from .neural_bd_filters import NeuralBlindDeconvolution
from .quadratic_cnn import QuadraticCNN


class FaultClassifier(nn.Module):
    """Clasificador de fallos simple para guiar la deconvolución."""

    def __init__(self, input_size: int = 64, num_classes: int = 4):
        """
        Args:
            input_size: Tamaño de características de entrada.
            num_classes: Número de clases de fallo (healthy, inner race, outer race, ball).
        """
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(input_size, 32),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Clasifica el tipo de fallo."""
        return self.fc(x)

    def predict(self, features: np.ndarray) -> int:
        """Predice la clase del fallo."""
        x = torch.tensor(features, dtype=torch.float32).unsqueeze(0)
        with torch.no_grad():
            logits = self.forward(x)
            return torch.argmax(logits, dim=1).item()


class ClassifierGuidedBD:
    """ClassBD: integración de BD neural con clasificador."""

    def __init__(self, temporal_length: int = 64, fft_size: int = 256, num_classes: int = 4):
        """
        Args:
            temporal_length: Longitud del filtro temporal.
            fft_size: Tamaño de FFT.
            num_classes: Número de clases de fallo.
        """
        self.quadratic_cnn = QuadraticCNN(num_layers=3)
        self.neural_bd = NeuralBlindDeconvolution(temporal_length, fft_size)
        self.classifier = FaultClassifier(input_size=64, num_classes=num_classes)
        self.fft_size = fft_size

    def extract_features(self, signal: np.ndarray) -> np.ndarray:
        """Extrae características de la señal."""
        fft_vals = np.fft.fft(signal, n=self.fft_size)
        magnitude = np.abs(fft_vals[: self.fft_size // 2])
        log_mag = np.log(magnitude + 1e-10)
        features = log_mag[:: len(magnitude) // 64]
        return features[:64]

    def diagnose(self, signal: np.ndarray) -> dict:
        """Realiza diagnóstico completo de fallo.

        Args:
            signal: Señal de vibración.

        Returns:
            Dict con deconvolución, características y clase de fallo.
        """
        signal = np.asarray(signal, dtype=np.float32)

        deconvolved = self.neural_bd.deconvolve(signal)

        features = self.extract_features(deconvolved)

        fault_class = self.classifier.predict(features)

        fault_names = ["Healthy", "Inner Race Fault", "Outer Race Fault", "Ball Fault"]

        return {
            "deconvolved_signal": deconvolved,
            "features": features,
            "fault_class": fault_class,
            "fault_name": fault_names[fault_class] if fault_class < len(fault_names) else "Unknown",
            "confidence": None,
        }

    def get_quadratic_cnn(self) -> QuadraticCNN:
        """Retorna el modelo Quadratic CNN."""
        return self.quadratic_cnn

    def get_classifier(self) -> FaultClassifier:
        """Retorna el clasificador."""
        return self.classifier
