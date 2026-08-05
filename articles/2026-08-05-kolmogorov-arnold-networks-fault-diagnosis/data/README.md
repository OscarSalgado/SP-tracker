# Datos Sintéticos para KAN Bearing Fault Diagnosis

Esta carpeta contiene datos sintéticos generados para demostración y validación.

## Generación

Ejecutar:
```bash
python data/generate_synthetic_vibration.py
```

Esto genera:
- `healthy.npy`: Señal de rodamiento sano
- `inner_race_fault.npy`: Señal con fallo en pista interna
- `outer_race_fault.npy`: Señal con fallo en pista externa
- `ball_fault.npy`: Señal con fallo en bola

## Características

Cada archivo contiene 2000 muestras de vibración a 20 kHz (0.1s de duración).
