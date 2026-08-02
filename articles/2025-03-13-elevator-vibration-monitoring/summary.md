# Monitoreo Online de Vibraciones Anormales en Ascensores mediante Gemelo Digital

## Objetivo

Desarrollar un sistema de detección online de vibraciones anormales en ascensores mediante un enfoque híbrido que combina: (1) un gemelo digital basado en simulación de elemento finito, (2) redes neuronales profundas mejoradas (ShuffleNetV2 con atención espacial-temporal), y (3) técnicas de adaptación de dominio para reducir la brecha entre datos simulados y medidos en tiempo real.

## Método

El trabajo propone una arquitectura en tres niveles:

1. **Modelado**: Construcción de un gemelo digital del ascensor mediante FEM que simula vibraciones anormales en guías de elevador (desalineamientos, pandeos, escalones). Se generan datos sintéticos de referencia.

2. **Detección y clasificación**:
   - Conversión de señales de aceleración 1D en espectrogramas 2D mediante transformada wavelet continua (CWT).
   - Extracción de características con ShuffleNetV2 mejorado con módulo de atención espacial-temporal (STAN) y activación Mish.
   - Adaptación de dominio profundo (DSAN) basada en funciones kernel de Gauss para alinear distribuciones entre datos simulados (fuente) y medidos (destino).

3. **Despliegue**: Sistema de monitoreo en tiempo real en dispositivos edge con comunicación MQTT/TCP hacia una plataforma de gemelo digital en Unity3D.

## Resultados principales

- **Precisión**: 98.2% en clasificación de cuatro tipos de anomalías (desalineamiento, pandeo, escalones, normal).
- **Comparación con modelos**: STAN supera a ShuffleNetV2 (92.8%), ResNet-18 (93.3%), GoogleNet (90.8%), MobileNetV2 (88.6%).
- **Eficiencia computacional**: 
  - Modelo de 1.258 MB (muy ligero para edge)
  - 0.152 GFLOPs
  - Tiempo de detección: 17 ms
  - Tiempo de respuesta de visualización: 110 ms
- **Impacto de mejoras**: Activación Mish (+1.1%), Atención Espacial-Temporal (+5.4%), Transferencia de aprendizaje (+0.7%).
- **Robustez**: DSAN mejora significativamente la generalización en múltiples condiciones de operación.

## Limitaciones

1. **Dependencia de FEM**: Requiere simulación precisa; inexactitudes en parámetros de rigidez/amortiguamiento degradan el desempeño.
2. **Escasez de datos reales etiquetados**: Recolectar vibraciones anormales reales es caro y peligroso, de ahí la necesidad de adaptación de dominio.
3. **Alcance limitado**: Se valida sobre 800 muestras de cuatro categorías; anomalías complejas o multi-tipo no se exploran.
4. **Variabilidad operacional**: Se asume cuatro estados de operación fijos; variabilidad en tipos de ascensores o velocidades variables podrían requerir re-entrenamiento.
5. **Latencia de visualización**: El impacto de la latencia del gemelo visual (Unity3D) en toma de decisiones de mantenimiento no se cuantifica.
