# Resumen

## Objetivo

Optimizar los parámetros dinámicos de un sistema de ascensor de tracción 2:1 para reducir la vibración y mejorar la calidad de viaje de los pasajeros. El problema es que los ascensores de alta velocidad experimentan una vibración excesiva, lo que afecta la comodidad y la salud de los pasajeros.

## Método

El artículo presenta un modelo dinámico vertical con 9 grados de libertad (9-DOF) para un ascensor de tracción tipo 2:1. Basándose en este modelo, se formula un problema de optimización que toma la amplitud de la aceleración vibratoria de la cabina como función objetivo. El método utiliza un **algoritmo genético con codificación dinámica de bytes** (Dynamic Byte Coding Genetic Algorithm), que combina las ventajas de la codificación binaria con la codificación de parámetros dinámicos para mejorar la eficiencia y robustez de la solución. La solución óptima se verifica mediante análisis de sensibilidad.

## Resultados principales

- Implementación exitosa en un sistema de ascensor de tracción 2:1 con problemas de vibración severa.
- Reducción del valor pico-pico de aceleración vibratoria vertical de 0.445 m/s² a 0.155 m/s² (aproximadamente 65% de reducción).
- Reducción del valor A95 (métrica de confort) de 0.396 m/s² a 0.082 m/s² (aproximadamente 79% de reducción).
- El algoritmo genético propuesto demuestra mayor eficiencia que métodos convencionales de codificación.

## Limitaciones

- El modelo se limita a 9 grados de libertad; una mayor precisión requeriría considerar más componentes.
- El estudio se enfoca únicamente en vibración vertical; la vibración horizontal no se considera.
- La precisión de la medición de parámetros dinámicos (rigidez, amortiguamiento, fuerzas de excitación) es crítica y afecta directamente los resultados; estos parámetros son difíciles de medir con precisión en la práctica.
