# Datos

## Generación de datos sintéticos

No existe dataset público disponible que reproduzca exactamente el escenario del artículo (caja de
engranajes con falla en rodamiento). Los datos se generan sintéticamente en el notebook.

### Composición de las señales sintéticas

Cada señal es una superposición de tres componentes:

1. **Componente periódica** (~70% de la energía): Simula fuerzas cinemáticas de engranajes.
   - 3 armónicos de la frecuencia de rotación fundamental (100 Hz base)
   - Amplitudes decrecientes (1.0, 0.5, 0.3)
   - Representa el "ruido operacional" dominante

2. **Componente aleatoria estacionaria** (~15% energía): Ruido blanco Gaussiano de baja amplitud.
   - σ = 0.1 × amplitud máxima periódica
   - Simula rozamiento, fricción inherente

3. **Componente transiente (impulsiva)** (~15% energía): Impulsos aislados simulando impactos.
   - 5-8 impactos en 2 segundos de registro
   - Envolventes suavizadas, amplitud ~0.8 × componente periódica
   - Modelan transitorios de fallo de rodamiento

### Parámetros de muestreo

- **Frecuencia de muestreo**: 10 kHz (típica en diagnóstico de máquinas rotativas)
- **Duración**: 2 segundos
- **Total de muestras**: 20,000

### Por qué son representativos

Estas componentes reflejan la estructura real de señales de vibración en máquinas:
- La componente periódica domina energéticamente (engranaje o eje que rota continuamente)
- El ruido estacionario es inevitable en mediciones reales
- Los transitorios son las "firmas" diagnósticas buscadas (fallos incipientes)

El desafío de separación es idéntico al del artículo original: extraer los transitorios débiles
debajo de una componente periódica fuerte y ruido, usando solo independencia estadística.
