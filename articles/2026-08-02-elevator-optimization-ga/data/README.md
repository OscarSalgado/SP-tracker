# Datos

## Datos sintéticos

No existe un dataset público específico para reproducir el estudio de caso del artículo, ya que
se trata de parámetros optimizados para un sistema de ascensor específico no divulgado públicamente.

### Generación de datos sintéticos

Los datos se generan directamente en `notebook.ipynb`:

1. **Parámetros del modelo**: Se definen valores típicos para un ascensor de tracción 2:1:
   - Masas (traction machine, counterweight, sheaves, cage, frame): 500-1500 kg cada una
   - Momentos de inercia de poleas: 50-150 kg·m²
   - Rigidez de muelles/cables: 1e5-5e5 N/m
   - Coeficientes de amortiguamiento: 1e3-5e3 N·s/m

2. **Excitación**: Se simula una excitación sinusoidal representativa del movimiento de arranque/parada
   del ascensor, con amplitud variable.

3. **Justificación de representatividad**: Estos valores están basados en órdenes de magnitud
   reportados en la literatura de dinámica de ascensores y en el propio artículo. El objetivo
   es demostrar cómo el algoritmo genético optimiza los parámetros para reducir la aceleración
   vibratoria máxima, comparable al resultado reportado (reducción de 0.445 a 0.155 m/s²).
