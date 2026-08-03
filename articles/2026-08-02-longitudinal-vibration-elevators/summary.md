# Resumen

## Objetivo

Desarrollar un modelo dinámico de múltiples grados de libertad (MDOF) preciso para predecir las vibraciones longitudinales en ascensores de alta velocidad causadas por excitaciones externas, y analizar cómo estos fenómenos afectan la seguridad estructural y el confort del pasajero.

## Método

El estudio utiliza el método de subestructura para descomponer el sistema de ascensor en subsistemas independientes (polea de tracción, sistema de tensionamiento, bastidor del coche, contrapeso y cables de acero segmentados). Mediante las ecuaciones de Lagrange y la segunda ley de Newton, se derivan ecuaciones diferenciales de movimiento acopladas que se integran en un modelo global. La validación se realiza comparando frecuencias naturales predichas con simulaciones de ADAMS (software de multidinámica) y contra un método Jacobi mejorado, mostrando convergencia dentro del 10%. Se resuelven las ecuaciones dinámicas usando el método Runge-Kutta de orden 4 con paso de tiempo variable.

## Resultados principales

1. **Excentricidad de polea**: Causa fluctuaciones periódicas con frecuencia de ~3.18 Hz. La aceleración pico se reduce de 46.6 mm/s² (sin carga) a 40.8 mm/s² (media carga) y 35.3 mm/s² (carga completa), atenuación de 24.2% bajo carga completa.

2. **Par de frenado inverso**: Genera un transiente de impacto corto (~4 s) seguido de oscilaciones amortiguadas. La aceleración bajo carga completa es ~15% superior a sin carga, con duración prolongada de vibraciones de baja frecuencia.

3. **Impacto en juntas de guía**: Provoca picos de aceleración instantánea que aumentan ~18% al pasar de 2 m/s a 6 m/s, con estrés en cables alcanzando 670-740 MPa.

4. **Sensibilidad de estrés en cables**: Altamente sensible a variaciones de carga en rango bajo (0-0.2), donde aumenta de ~150 MPa a ~300 MPa. En rango alto (0.8-1.0) la tasa de crecimiento se estabiliza.

## Limitaciones

- Assume carga uniformemente distribuida en los cables (en práctica hay desequilibrio por desgaste asimétrico).
- Validación enfocada en frecuencias naturales, no en respuesta de aceleración bajo excitaciones reales.
- Coeficientes de fricción y amortiguamiento asumidos constantes (insensibles a temperatura y deslizamiento).
- Modelo no incluye efectos aerodinámicos ni irregularidades del carril (solo saltos discretos en juntas).
- Requerirá validación experimental futura en instalaciones controladas para corroborar comportamiento bajo carga real.
