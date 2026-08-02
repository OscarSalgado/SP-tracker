# Datos del artículo

## Procedencia

Los datos utilizados en este artículo son **sintéticos**, generados mediante la integración numérica del modelo dinámico MDOF descrito en el paper. No se disponibilizan datasets públicos del comportamiento de ascensores reales bajo excitaciones externas controladas debido a las restricciones de seguridad operativa y confidencialidad de las instalaciones de elevadores.

## Generación de datos sintéticos

El script `generate_synthetic_data.py` (ubicado en `src/`) simula las tres fuentes de excitación Externa investigadas:

1. **Excentricidad de polea**: Desplazamiento armónico de amplitud 3 mm a frecuencia de rotación (≈3.18 Hz a v=6 m/s)
2. **Par de frenado inverso**: Perfil de torque piecewise compuesto por:
   - Fase de aceleración inicial
   - Fase de estado estable
   - Fase de decaimiento exponencial
3. **Impacto en juntas de guía**: Secuencia de pulsos de desplazamiento separados por el espaciamiento estándar de carriles (1 m)

## Parámetros del sistema simulado

Se utilizan los parámetros de un ascensor real de alta velocidad (Tabla 2 del paper):
- Masa del coche: 2282 kg
- Masa del contrapeso: 4887.4 kg
- Rigidez de aislantes: 1.6 × 10⁵ N/m (tracción), 9.8 × 10⁵ N/m (contrapeso)
- 15 cables de tracción con densidad 0.494 kg/m
- Velocidad de funcionamiento: 6 m/s (nominal)

## Representatividad

Los datos sintéticos reproducen fielmente el comportamiento modal y la respuesta transitoria observada en la simulación ADAMS validada en el artículo. Son representativos de:

- Oscilaciones bajo excitación periódica continu (excentricidad)
- Respuesta impulsiva y amortiguamiento estructural (frenado)
- Fenómenos transientes de corta duración (impacto en juntas)

## Limitaciones

- No incluyen fricción variable ni efectos de temperatura
- Asumen continuidad de contacto en juntas (sin despegue)
- No capturan deformación plástica ni degradación de componentes
- Representan un ciclo operativo aislado, no fatiga acumulada

## Uso en el notebook

El notebook `notebook.ipynb` genera estos datos bajo demanda y los procesa para producir visualizaciones comparables con las del artículo original (Figuras 9-15).
