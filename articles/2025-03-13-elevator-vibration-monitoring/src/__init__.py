"""Detección de vibraciones anormales en ascensores con STAN y DSAN.

Implementa ShuffleNetV2 mejorado con Spatial-Temporal Attention (STAN)
y Deep Subdomain Adaptation Network (DSAN) para clasificación de
vibraciones de ascensores con adaptación de dominio.
"""

from .models import DomainAdaptationModule, ShuffleNetV2STAN
from .preprocessing import CWTTransform

__all__ = [
    "ShuffleNetV2STAN",
    "DomainAdaptationModule",
    "CWTTransform",
]
