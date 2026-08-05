"""Kolmogorov-Arnold Networks for bearing fault diagnosis.

Implementación del método de Rigas et al. (arXiv:2412.01322):
- Redes Kolmogorov-Arnold con funciones de activación aprendibles.
- Selección automática de características.
- Clasificación interpretable de tipos de fallo.
"""

from .kan import BearingFaultDiagnoser, KANFaultClassifier, KANLayer

__all__ = [
    "KANLayer",
    "KANFaultClassifier",
    "BearingFaultDiagnoser",
]
