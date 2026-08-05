"""Red convolucional cuadrática para extracción de impulsos periódicos."""

import torch
import torch.nn as nn


class QuadraticCNN(nn.Module):
    """CNN cuadrática para extraer impulsos periódicos de fallos.

    Utiliza operaciones de convolución cuadrática para amplificar
    impulsos característicos de fallos en rodamientos.
    """

    def __init__(self, num_layers: int = 3, kernel_size: int = 5):
        """
        Args:
            num_layers: Número de capas convolucionales.
            kernel_size: Tamaño del kernel.
        """
        super().__init__()
        self.num_layers = num_layers
        self.kernel_size = kernel_size

        self.layers = nn.ModuleList()
        padding = (kernel_size - 1) // 2

        for i in range(num_layers):
            in_channels = 1 if i == 0 else 32
            out_channels = 32

            conv = nn.Conv1d(in_channels, out_channels, kernel_size, padding=padding)
            self.layers.append(conv)

        self.output_layer = nn.Conv1d(32, 1, kernel_size, padding=padding)
        self.relu = nn.ReLU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass con activación cuadrática.

        Args:
            x: Tensor de entrada (batch, channels, length).

        Returns:
            Tensor de salida (batch, 1, length).
        """
        for layer in self.layers:
            x = layer(x)
            x = x**2
            x = self.relu(x)

        return self.output_layer(x)

    def predict(self, signal: list) -> list:
        """Predicción en una señal."""
        x = torch.tensor([signal], dtype=torch.float32).unsqueeze(1)
        with torch.no_grad():
            output = self.forward(x)
        return output.squeeze().numpy().tolist()
