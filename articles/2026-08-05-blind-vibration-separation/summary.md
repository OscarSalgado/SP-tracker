# Resumen

## Objetivo

Detectar tempranamente fallos en rodamientos de maquinaria rotatoria mediante la **separación ciega de fuentes de vibración**. El desafío radica en que las vibraciones de engranajes (dominantes) y de rodamientos (débiles) se mezclan en el trayecto hacia el sensor, distorsionadas por la función de transferencia del equipo. El método propuesto elimina la necesidad de información previa sobre el equipo o mediciones externas.

## Método

El enfoque usa **dos etapas**:

1. **Estimación de vibración de engranajes**: Se entrena una **CNN dilated** para aislar la señal dominante de engranajes usando la envolvente espectral.

2. **Estimación de vibración de rodamiento**: Se estima a partir del residuo (diferencia), usando la envolvente logarítmica al cuadrado.

3. **Deconvolución**: Se aplica un nuevo método denominado **Whitening-Based Deconvolution (WBD)** para eliminar el efecto de la función de transferencia de ambas fuentes.

**Librerías**: PyTorch/TensorFlow (CNN), NumPy, SciPy (procesamiento de señales).

## Resultados principales

- **Detección temprana de fallos**: El método detecta anomalías en rodamientos en etapas iniciales cuando no hay información externa disponible.
- **Validación dual**: Resultados tanto en datos simulados como en experimentos reales demuestran la viabilidad.
- **Robustez**: La separación ciega funciona sin calibración previa del equipo.

## Limitaciones

- **Depende de ruido**: Rendimiento degradado bajo ruido muy alto (aunque manejaable con preprocesamiento).
- **Complejidad computacional**: El entrenamiento de la CNN requiere datasets etiquetados representativos.
- **Máquinas específicas**: La arquitectura se validó en configuraciones de maquinaria rotatoria específicas; generalización a otros tipos requiere reentrenamiento.
