# Resumen

## Objetivo

Desarrollar un marco interpretable para la clasificación automática del estado operacional de
ascensores a partir de señales de un acelerómetro (eje Z), con aplicaciones en monitoreo de salud
estructural, diagnósticos y mantenimiento predictivo de sistemas de transporte vertical.

## Método

Se propone una red neuronal convolucional unidimensional (1D CNN) que procesa exclusivamente
señales del eje Z de un acelerómetro instalado en una cabina de ascensor. El modelo está diseñado
para clasificar distintos estados operacionales: movimiento ascendente, movimiento descendente,
parada, apertura de puertas y cierre de puertas. El trabajo incluye una fase de interpretabilidad
que expone cómo la red extrae características físicamente significativas de las señales de
aceleración, vinculando el aprendizaje de patrones con fenómenos mecánicos reales (inercia,
fricción, aceleraciones de cambio de dirección).

## Resultados principales

El modelo fue validado sobre un conjunto de datos capturado en operación real, consistente en 250
viajes de ascensor completos. Fue comparado contra tres métodos de clasificación alternativos
(métodos clásicos de aprendizaje automático), demostrando mayor precisión y capacidad de
generalización. La interpretabilidad revela que los filtros de la CNN actúan como detectores de
transiciones y cambios de aceleración característicos de cada estado.

## Limitaciones

Los datos de validación proceden de un único edificio/instalación, lo que puede limitar la
generalización a otros tipos de ascensores o configuraciones mecánicas. El enfoque depende de la
calidad y sincronización del acelerómetro, y no se explora robustez ante ruido o fallo del sensor.
La investigación se centra en ascensores convencionales y no cubre variantes especiales (montacargas,
plataformas inclinadas, etc.).
