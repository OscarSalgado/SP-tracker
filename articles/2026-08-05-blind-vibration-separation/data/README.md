# Datos

## Descripción

Los datos utilizados para validar el método de separación ciega de vibración son **sintéticos**,
generados para reproducir el comportamiento observado en maquinaria rotatoria real.

## Generación de datos sintéticos

### Justificación

- **Realisticidad**: Se modelan dos fuentes independientes (engranaje + rodamiento) basadas en
  características espectrales y temporales reportadas en literatura.
- **Controlabilidad**: Permite evaluar el método bajo condiciones controladas (SNR variable,
  niveles de ruido, funciones de transferencia conocidas).
- **Reproducibilidad**: Cualquiera puede regenerar los datos con el mismo script sin dependencias
  externas.

### Componentes

1. **Vibración de engranaje** (componente dominante):
   - Frecuencia fundamental: ~100 Hz
   - Amplitud: 1.0 V
   - Incluye armónicos característicos

2. **Vibración de rodamiento** (componente débil, indicador de fallo):
   - Frecuencia de paso de bola: ~60 Hz (característica de rodamiento)
   - Amplitud: 0.1 V (débil respecto a engranaje)
   - Indica etapa inicial de degradación

3. **Función de transferencia del sistema**:
   - Modelada como un filtro paso-bajo de orden 2
   - Simula la distorsión introducida por el montaje y sensores

### Generación

Ejecutar:
```bash
python data/generate_synthetic_vibration.py
```

Genera archivos:
- `gear_vibration.npy`: Vibración de engranaje pura (sin distorsión)
- `bearing_vibration.npy`: Vibración de rodamiento pura
- `mixed_signal.npy`: Señal mezclada (observada)
- `transfer_function.npy`: Función de transferencia aplicada

### Parámetros configurables

Editar `generate_synthetic_vibration.py`:
- `sampling_rate`: Frecuencia de muestreo (Hz)
- `duration`: Duración de la señal (segundos)
- `snr_db`: Relación señal a ruido (dB)
- `freq_gear`: Frecuencia fundamental de engranaje (Hz)
- `freq_bearing`: Frecuencia de paso de bola (Hz)

