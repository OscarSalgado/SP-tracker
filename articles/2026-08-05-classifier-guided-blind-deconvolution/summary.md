# Resumen

## Objetivo

Diagnosticar fallos en rodamientos bajo **condiciones de ruido severo** mediante deconvolución ciega guiada por un clasificador. El desafío es que la deconvolución ciega tradicional y el aprendizaje profundo tienen objetivos conflictivos; este artículo propone una solución conjunta (ClassBD) que integra ambos.

## Método

**ClassBD** (Classifier-guided Blind Deconvolution) utiliza:

1. **Filtro de dominio temporal**: Red convolucional cuadrática (Quadratic CNN) para extraer impulsos periódicos característicos de fallos
2. **Filtro de dominio frecuencial**: Red neuronal completamente conectada para amplificar componentes discretos de frecuencia
3. **Entrenamiento conjunto**: La guía del clasificador asegura que los filtros extraigan características relevantes para diagnóstico

**Arquitectura**: Módulo de denoising physics-informed que combina principios físicos (deconvolución) con capacidad de aprendizaje (deep learning).

## Resultados principales

- Desempeño superior bajo ruido alto (SNR bajo) comparado con métodos tradicionales
- La integración de BD y clasificador mejora la tasa de diagnóstico
- Robustez demostrada en múltiples tipos de fallos de rodamiento (inner race, outer race, ball)
- Generalización a diferentes condiciones operativas

## Limitaciones

- Requiere etiquetado de fallos para entrenar el clasificador
- Validación enfocada en condiciones de laboratorio controladas
- Generalización a máquinas muy diferentes podría requerer reentrenamiento
