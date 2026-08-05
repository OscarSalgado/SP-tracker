"""Kolmogorov-Arnold Network for bearing fault diagnosis."""

import numpy as np
import torch
import torch.nn as nn


class KANLayer(nn.Module):
    """Kolmogorov-Arnold Layer with learnable univariate functions."""

    def __init__(self, input_dim: int, output_dim: int, grid_size: int = 5):
        """
        Args:
            input_dim: Input dimension.
            output_dim: Output dimension.
            grid_size: Grid size for piecewise linear approximation.
        """
        super().__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.grid_size = grid_size

        self.weight = nn.Parameter(torch.randn(output_dim, input_dim, grid_size) * 0.1)
        self.bias = nn.Parameter(torch.zeros(output_dim))
        self.grid = nn.Parameter(torch.linspace(-2, 2, grid_size), requires_grad=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Apply KAN layer with piecewise linear activations."""
        batch_size = x.shape[0]
        output = torch.zeros(batch_size, self.output_dim, device=x.device)

        for o in range(self.output_dim):
            for i in range(self.input_dim):
                # Piecewise linear basis: evaluate x[i] on grid
                basis = self._piecewise_basis(x[:, i])
                output[:, o] += torch.matmul(basis, self.weight[o, i, :])

        return output + self.bias

    def _piecewise_basis(self, x: torch.Tensor) -> torch.Tensor:
        """Compute piecewise linear basis functions."""
        batch_size = x.shape[0]
        basis = torch.zeros(batch_size, self.grid_size, device=x.device)

        for i in range(self.grid_size - 1):
            x_low = self.grid[i]
            x_high = self.grid[i + 1]
            mask = (x >= x_low) & (x <= x_high)
            if mask.any():
                basis[mask, i] = 1 - torch.abs(x[mask] - (x_low + x_high) / 2) / (x_high - x_low)

        basis[:, -1] = torch.clamp(1 - torch.abs(x - self.grid[-1]), 0, 1)
        return basis


class KANFaultClassifier(nn.Module):
    """Kolmogorov-Arnold Network for bearing fault classification."""

    def __init__(self, input_size: int = 64, num_classes: int = 5, grid_size: int = 5):
        """
        Args:
            input_size: Input feature dimension.
            num_classes: Number of fault classes.
            grid_size: Grid size for KAN activations.
        """
        super().__init__()
        self.input_size = input_size
        self.num_classes = num_classes

        self.layer1 = KANLayer(input_size, 32, grid_size)
        self.layer2 = KANLayer(32, 16, grid_size)
        self.layer3 = KANLayer(16, num_classes, grid_size)

        self.relu = nn.ReLU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Classify fault type."""
        x = self.layer1(x)
        x = self.relu(x)
        x = self.layer2(x)
        x = self.relu(x)
        x = self.layer3(x)
        return x

    def predict(self, features: np.ndarray) -> int:
        """Predict fault class from features."""
        x = torch.tensor(features, dtype=torch.float32).unsqueeze(0)
        with torch.no_grad():
            logits = self.forward(x)
            return torch.argmax(logits, dim=1).item()


class BearingFaultDiagnoser:
    """Bearing fault diagnosis using KAN."""

    def __init__(self, input_size: int = 64, grid_size: int = 5):
        """
        Args:
            input_size: Input feature dimension.
            grid_size: Grid size for KAN layers.
        """
        self.kan_classifier = KANFaultClassifier(input_size, num_classes=5, grid_size=grid_size)
        self.input_size = input_size

    def extract_features(self, signal: np.ndarray) -> np.ndarray:
        """Extract features from vibration signal."""
        fft_vals = np.fft.fft(signal)
        magnitude = np.abs(fft_vals[: len(signal) // 2])
        log_mag = np.log(magnitude + 1e-10)
        features = log_mag[:: len(magnitude) // self.input_size]
        return features[: self.input_size]

    def diagnose(self, signal: np.ndarray) -> dict:
        """Diagnose bearing fault.

        Args:
            signal: Vibration signal.

        Returns:
            Dict with fault class, name, and confidence.
        """
        signal = np.asarray(signal, dtype=np.float32)
        features = self.extract_features(signal)

        fault_class = self.kan_classifier.predict(features)
        fault_names = ["Healthy", "Inner Race", "Outer Race", "Ball", "Combination"]

        return {
            "features": features,
            "fault_class": fault_class,
            "fault_name": fault_names[fault_class] if fault_class < len(fault_names) else "Unknown",
            "confidence": None,
        }
