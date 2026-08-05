"""CNN dilated para separación de vibración de engranajes."""

import torch
import torch.nn as nn


class DilatedCNN(nn.Module):
    """CNN con convoluciones dilatadas para aislamiento de señal de engranajes.

    Arquitectura inspirada en WaveNet y arquitecturas dilated.
    """

    def __init__(self, input_channels: int = 1, output_channels: int = 1, num_layers: int = 4):
        """
        Args:
            input_channels: Canales de entrada (1 para señal mono).
            output_channels: Canales de salida (1 para salida mono).
            num_layers: Número de capas dilated.
        """
        super().__init__()
        self.input_channels = input_channels
        self.output_channels = output_channels
        self.num_layers = num_layers

        self.layers = nn.ModuleList()
        for layer_idx in range(num_layers):
            dilation = 2**layer_idx
            kernel_size = 3
            padding = (kernel_size - 1) * dilation // 2

            conv = nn.Conv1d(
                in_channels=input_channels if layer_idx == 0 else 64,
                out_channels=64,
                kernel_size=kernel_size,
                padding=padding,
                dilation=dilation,
                bias=True,
            )
            self.layers.append(conv)

        self.output_layer = nn.Conv1d(64, output_channels, kernel_size=1)
        self.relu = nn.ReLU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass.

        Args:
            x: Tensor de entrada shape (batch, channels, length).

        Returns:
            Tensor de salida shape (batch, output_channels, length).
        """
        for layer in self.layers:
            x = self.relu(layer(x))

        return self.output_layer(x)

    def predict(self, signal: list) -> list:
        """Predicción sobre una señal (interfaz compatible con tests).

        Args:
            signal: Lista de valores numéricos.

        Returns:
            Lista de valores predichos.
        """
        x = torch.tensor([signal], dtype=torch.float32).unsqueeze(1)
        with torch.no_grad():
            output = self.forward(x)
        return output.squeeze().numpy().tolist()
