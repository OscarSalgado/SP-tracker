# Datos

## Datos públicos vs. sintéticos

El artículo original fue validado sobre un dataset privado de 250 viajes de ascensor capturados
in situ, con datos de acelerómetro del eje Z. **Este dataset no es públicamente accesible** (datos
propietarios de operación industrial).

Por este motivo, `notebook.ipynb` **genera datos sintéticos** que representan los cinco estados
operacionales del ascensor:

1. **moving_up**: Aceleración inicial, velocidad constante, desaceleración. Señal característica
   de cambios de aceleración positivos.
2. **moving_down**: Similar a *moving_up* pero con aceleraciones negativas.
3. **stopped**: Señal con baja varianza, cercana a cero (ruido de fondo).
4. **doors_opening**: Transición rápida de aceleración con patrones oscilatorios.
5. **doors_closing**: Similar a *doors_opening* con otra firma de frecuencia.

## Generación de datos sintéticos

Los datos sintéticos se generan mediante combinaciones de:
- Segmentos de aceleración/desaceleración (rampas lineales + ruido gaussiano)
- Oscilaciones (senos/cosenos con frecuencias características)
- Ruido gaussiano de fondo

Esta representación captura los **fenómenos físicos esenciales** que la CNN debe aprender para
distinguir estados: transiciones de aceleración (derivada), patrones oscilativos (frecuencias
características de mecanismos de puertas), y nivel de ruido base.

## Reproducibilidad

El notebook `notebook.ipynb` genera estos datos con una semilla fija (`np.random.seed(42)`),
garantizando que los resultados sean reproducibles entre ejecuciones.
