# Resumen

## Objetivo

Proponer técnicas robustas de separación ciega de componentes en señales de vibración que adapten
los principios de Blind Source Separation (BSS) a problemas reales de ingeniería mecánica. El
objetivo pragmático es descomponer una señal de vibración en: (1) componentes periódicas
(relacionadas con mecanismos rotativos), (2) componentes aleatorias estacionarias (ruido de fondo),
y (3) componentes aleatorias no-estacionarias (transitorios impulsivos como fallos).

## Método

El artículo propone dos algoritmos basados en la Transformada de Fourier a Corto Plazo (STFT):

1. **Extracción de componentes periódicos**: Utiliza un filtro predictor que explota el hecho de
   que las componentes periódicas son perfectamente predecibles en el futuro (correlación temporal
   infinita), mientras que las componentes aleatorias se hacen impredecibles conforme aumenta el
   retraso temporal.

2. **Extracción de componentes transitorios**: Basada en la **curtosis espectral**, una medida de
   la desviación de la Gaussianidad en el dominio de frecuencias que identifica automáticamente
   las bandas de frecuencia con mayor grado de impulsividad (transitorios).

Ambos algoritmos operan en el dominio de Fourier para manejar eficientemente mezclas convolutivas
con respuestas impulsionales largas características de sistemas mecánicos.

## Resultados principales

- Demostración exitosa en caja de engranajes con falla en rodamiento: el método extrae
  componentes periódicas debidas al engranaje, exponiendo claramente los transitorios impulsivos
  causados por el fallo del rodamiento.
- Aplicación a señales de un vehículo ferroviario: revela transitorios de impacto ~50 veces más
  pequeños que la señal original, imposibles de detectar a simple vista en la señal cruda.
- El enfoque es general y aplicable a diagnóstico de máquinas rotativas, análisis modal de
  sistemas mecánicos y otras aplicaciones con señales complejas.

## Limitaciones

- El método retorna solo tres subconjuntos de componentes; se requieren técnicas adicionales
  (análisis espectral clásico o análisis tiempo-frecuencia) para discriminar entre contribuciones
  independientes dentro de cada subconjunto.
- Basado en mediciones de salida única (SISO). Los autores señalan que se espera mejor desempeño
  con múltiples salidas (MIMO).
- Las dificultades fundamentales del BSS aplicado a vibraciones (convolutividad, número de fuentes
  desconocido, fuentes distribuidas espacialmente) se alivian pero no se resuelven completamente:
  es un enfoque pragmático, no ideal.
- La separación depende de que los componentes difieran significativamente en sus características
  estadísticas (periodicidad, estacionariedad). Señales con comportamientos superpuestos pueden
  ser difíciles de descomponer.
