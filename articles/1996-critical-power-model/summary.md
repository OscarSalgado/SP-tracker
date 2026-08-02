# Resumen

## Objetivo

El artículo propone una extensión del modelo clásico de potencia crítica (CP) mediante la introducción de un tercer parámetro. El modelo estándar de 2 parámetros asume una asíntota temporal en t=0, pero evidencia empírica sugiere que el modelo sobrestima la potencia crítica e infraestima la capacidad anaeróbica de trabajo (AWC). Este trabajo relaja esa restricción para obtener estimaciones más precisas.

## Método

Morton desarrolla un modelo hiperbólico generalizado permitiendo una asíntota temporal no nula (t=k):

- **Modelo 2-parámetros (estándar)**: (P - CP)·t = AWC
- **Modelo 3-parámetros**: (P - CP)·(t - k) = AWC

Aplica regresión no lineal con mínimos cuadrados ponderados sobre datos de 14 sujetos del estudio de McLellan y Cheung (1992), comparando el ajuste de ambos modelos. El tercer parámetro k es interpretable biológicamente como una asíntota temporal negativa que permite identificar una potencia instantánea máxima (P_max).

## Resultados principales

1. En 13 de 14 sujetos, k es significativamente menor que cero (p < 0.05), demostrando que el modelo 3-parámetros es estadísticamente superior.
2. Estimaciones de AWC con el modelo 3-parámetros son **significativamente mayores** (p < 0.01) que con el modelo estándar.
3. Estimaciones de CP son **significativamente menores** (p < 0.05) con el nuevo modelo, alineándose mejor con tiempos de exhaustación observados.
4. El residual medio cuadrado (RMS) es significativamente menor (p < 0.05) con el modelo 3-parámetros, indicando mejor ajuste.
5. Identifica un parámetro biológicamente significativo (P_max) que representa la potencia máxima instantánea derivada del corte de la hipérbola en el eje de potencia.

## Resultados derivados

A partir del nuevo modelo, Morton propone una hipótesis: la potencia máxima que puede desarrollarse en cualquier instante es **proporcional linealmente a la cantidad de capacidad anaeróbica disponible** en ese momento. Esto implica que **no toda la AWC se consume necesariamente en el punto de exhaustación**, corrigiendo una asunción del modelo clásico.

## Limitaciones

- Los datos provienen de un único estudio (McLellan & Cheung, 1992) con n=14 sujetos.
- El modelo requiere selección más cuidadosa de los puntos de potencia de prueba (spread más amplio: desde muy altos hasta muy bajos tiempos de exhaustación).
- Los errores estándar son frecuentemente mayores para AWC y CP en el modelo 3-parámetros respecto al 2-parámetros, sugiriendo mayor sensibilidad a la selección de datos.
- La validación cruzada en otras muestras y modalidades de ejercicio (natación, carrera) aún está pendiente.
