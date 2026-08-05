"""Classifier-guided Blind Deconvolution para diagnóstico de fallos en rodamientos.

Implementación del método de Liao et al. (arXiv:2404.15341):
- Quadratic CNN para extracción de impulsos periódicos
- Filtros neurales en dominio temporal y frecuencial
- Clasificador de fallos integrado
"""

from .classifier_guided_bd import ClassifierGuidedBD, FaultClassifier
from .neural_bd_filters import NeuralBlindDeconvolution
from .quadratic_cnn import QuadraticCNN

__all__ = [
    "ClassifierGuidedBD",
    "QuadraticCNN",
    "NeuralBlindDeconvolution",
    "FaultClassifier",
]
