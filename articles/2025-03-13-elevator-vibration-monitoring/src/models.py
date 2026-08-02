"""Arquitectura de red neuronal STAN + DSAN para detección de vibraciones."""

import torch
import torch.nn as nn
import torch.nn.functional as F


class Mish(nn.Module):
    """Función de activación Mish: x * tanh(softplus(x))."""

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x * torch.tanh(F.softplus(x))


class ChannelAttention(nn.Module):
    """Módulo de atención de canales."""

    def __init__(self, channels: int, reduction: int = 16):
        super().__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.max_pool = nn.AdaptiveMaxPool2d(1)
        self.fc = nn.Sequential(
            nn.Conv2d(channels, channels // reduction, 1, bias=False),
            Mish(),
            nn.Conv2d(channels // reduction, channels, 1, bias=False),
        )
        self.sigmoid = nn.Sigmoid()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        avg_out = self.fc(self.avg_pool(x))
        max_out = self.fc(self.max_pool(x))
        out = avg_out + max_out
        return self.sigmoid(out)


class SpatialAttention(nn.Module):
    """Módulo de atención espacial."""

    def __init__(self, kernel_size: int = 7):
        super().__init__()
        padding = kernel_size // 2
        self.conv = nn.Conv2d(2, 1, kernel_size, padding=padding, bias=False)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        avg_out = torch.mean(x, dim=1, keepdim=True)
        max_out, _ = torch.max(x, dim=1, keepdim=True)
        x_cat = torch.cat([avg_out, max_out], dim=1)
        out = self.conv(x_cat)
        return self.sigmoid(out)


class ShuffleBlock(nn.Module):
    """Bloque de shuffle de ShuffleNetV2 con atención."""

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        stride: int = 1,
        groups: int = 1,
    ):
        super().__init__()
        self.stride = stride
        self.groups = groups

        hidden_channels = out_channels // 2

        self.branch1 = nn.Sequential(
            nn.Conv2d(in_channels // 2, hidden_channels, 3, stride, 1, groups=groups, bias=False),
            nn.BatchNorm2d(hidden_channels),
            Mish(),
        )

        self.branch2 = nn.Sequential(
            nn.Conv2d(in_channels // 2, hidden_channels, 1, bias=False),
            nn.BatchNorm2d(hidden_channels),
            Mish(),
            nn.Conv2d(hidden_channels, hidden_channels, 3, stride, 1, groups=groups, bias=False),
            nn.BatchNorm2d(hidden_channels),
            Mish(),
        )

        self.ca = ChannelAttention(out_channels)
        self.sa = SpatialAttention()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.stride == 1:
            x1, x2 = x.chunk(2, 1)
            out = torch.cat([self.branch1(x1), self.branch2(x2)], 1)
        else:
            x1, x2 = x.chunk(2, 1)
            out = torch.cat([self.branch1(x1), self.branch2(x2)], 1)

        out = out * self.ca(out)
        out = out * self.sa(out)
        return out


class ShuffleNetV2STAN(nn.Module):
    """ShuffleNetV2 mejorado con Spatial-Temporal Attention Network (STAN).

    Clasificador de vibraciones anormales en ascensores optimizado para
    despliegue en dispositivos edge.
    """

    def __init__(self, num_classes: int = 4, input_channels: int = 3):
        super().__init__()
        self.input_channels = input_channels
        self.num_classes = num_classes

        self.conv1 = nn.Sequential(
            nn.Conv2d(input_channels, 24, 3, 2, 1, bias=False),
            nn.BatchNorm2d(24),
            Mish(),
        )

        self.layer1 = self._make_layer(24, 58, 3, 1)
        self.layer2 = self._make_layer(58, 116, 7, 2)
        self.layer3 = self._make_layer(116, 232, 3, 2)
        self.layer4 = self._make_layer(232, 464, 3, 2)

        self.conv5 = nn.Sequential(
            nn.Conv2d(464, 1024, 1, 1, 0, bias=False),
            nn.BatchNorm2d(1024),
            Mish(),
        )

        self.global_pool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(1024, num_classes)

    def _make_layer(
        self,
        in_channels: int,
        out_channels: int,
        num_blocks: int,
        stride: int,
    ) -> nn.Sequential:
        layers = []
        for i in range(num_blocks):
            s = stride if i == 0 else 1
            layers.append(
                ShuffleBlock(in_channels if i == 0 else out_channels, out_channels, s),
            )
        return nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.conv1(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.conv5(x)
        x = self.global_pool(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x

    def extract_features(self, x: torch.Tensor) -> torch.Tensor:
        """Extrae características antes de la capa final."""
        x = self.conv1(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.conv5(x)
        x = self.global_pool(x)
        x = x.view(x.size(0), -1)
        return x


class DomainAdaptationModule(nn.Module):
    """Módulo de adaptación de dominio profundo (DSAN) con kernel de Gauss.

    Reduce la diferencia de distribución entre dominio fuente (datos simulados)
    y dominio destino (datos medidos reales) mediante Maximum Mean Discrepancy
    basado en kernel de Gauss.
    """

    def __init__(self, feature_dim: int = 1024, num_classes: int = 4):
        super().__init__()
        self.feature_dim = feature_dim
        self.num_classes = num_classes
        self.classifier = nn.Linear(feature_dim, num_classes)

    def compute_mmd_loss(
        self,
        source_features: torch.Tensor,
        target_features: torch.Tensor,
    ) -> torch.Tensor:
        """Calcula MMD (Maximum Mean Discrepancy) con kernel RBF."""
        kernel_values = [0.2, 0.5, 1.0, 2.0]
        loss = 0.0

        for kv in kernel_values:
            source_kernel = self._rbf_kernel(source_features, source_features, kv)
            target_kernel = self._rbf_kernel(target_features, target_features, kv)
            cross_kernel = self._rbf_kernel(source_features, target_features, kv)

            mmd = source_kernel.mean() + target_kernel.mean() - 2 * cross_kernel.mean()
            loss += torch.clamp(mmd, min=0.0)

        return loss / len(kernel_values)

    @staticmethod
    def _rbf_kernel(x: torch.Tensor, y: torch.Tensor, gamma: float) -> torch.Tensor:
        """Calcula matriz de kernel RBF."""
        xx = (x**2).sum(dim=1, keepdim=True)
        yy = (y**2).sum(dim=1, keepdim=True)
        xy = torch.matmul(x, y.t())
        distances = xx + yy.t() - 2 * xy
        distances = torch.clamp(distances, min=0.0)
        return torch.exp(-gamma * distances)

    def forward(
        self,
        source_features: torch.Tensor,
        source_labels: torch.Tensor,
        target_features: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Calcula predicciones y pérdida de adaptación de dominio.

        Returns:
            tuple: (logits, mmd_loss)
        """
        logits = self.classifier(source_features)
        mmd_loss = self.compute_mmd_loss(source_features, target_features)
        return logits, mmd_loss
