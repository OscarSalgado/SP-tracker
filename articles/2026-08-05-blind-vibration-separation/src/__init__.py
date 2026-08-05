"""Separación ciega de fuentes de vibración usando Deep Learning y Deconvolución.

Implementación del método de Makienko et al. (arXiv:2405.12774):
- CNN dilated para aislamiento de vibración de engranajes
- Whitening-Based Deconvolution (WBD) para eliminar función de transferencia
"""

from .dilated_cnn import DilatedCNN
from .vibration_separator import VibrationSeparator
from .whitening_deconvolution import WhiteningBasedDeconvolution

__all__ = [
    "DilatedCNN",
    "VibrationSeparator",
    "WhiteningBasedDeconvolution",
]
