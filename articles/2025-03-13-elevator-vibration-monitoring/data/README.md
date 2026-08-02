# Datos: Monitoreo de Vibraciones en Ascensores

El sistema utiliza dos fuentes de datos complementarias:

## 1. Dataset público: CWRU (Case Western Reserve University)

**Descripción**: Datos de aceleración medidos reales de rodamientos bajo diferentes condiciones operativas.

- **Fuente**: [CWRU Bearing Data Center](https://csegroups.case.edu/bearingdatacenter/home)
- **Licencia**: Datos públicos sin restricción para uso académico/investigación
- **Frecuencia de muestreo**: 12 kHz
- **Resolución**: 0.021 pulgadas (aproximadamente 0.533 mm)
- **Características**: 
  - 800 muestras etiquetadas bajo cada condición de operación
  - Aceleración medida en tres ejes (vertical, horizontal, axial)
  - Condiciones de operación: 4 estados de velocidad/carga (Con_1 a Con_4)

**Descarga**:
```bash
# El dataset se descarga automáticamente en notebook.ipynb
# Alternativamente, acceso directo en:
# https://csegroups.case.edu/bearingdatacenter/files/gearbox%20fault%20detection%20experimental%20data.zip
```

**Procesamiento en el notebook**:
- Normalización de señales (media 0, varianza 1)
- Segmentación en ventanas de 4096 muestras con 50% de superposición
- Transformación a espectrogramas mediante CWT (Continuous Wavelet Transform)
- Redimensionamiento a 224×224 píxeles para entrada de red

## 2. Datos sintéticos: Simulación FEM (Finite Element Method)

**Descripción**: Señales simuladas mediante análisis de elemento finito para modelar vibraciones anormales en guías de ascensores.

- **Generación**: Script Python con FEM basado en parámetros físicos del artículo
- **Parámetros simulados**:
  - Desalineamiento de guías: ±10 mm a ±100 mm
  - Pandeo de guías: curvatura variable
  - Escalones en guías: saltos discretos de altura
  - Ruido blanco gaussiano añadido a ~10 dB SNR

**Representatividad**:
El artículo reporta que los datos simulados capturan las características espectrales clave de las vibraciones anormales:
- Contenido espectral en rango 0-100 Hz
- Transitorios causados por impactos discretos (escalones)
- Modulación de amplitud por desalineamientos
- Cuando se alinean con datos CWRU reales mediante DSAN, logran 98.2% de precisión en clasificación

**Generación en el notebook**:
```python
# Simulación simplificada de vibraciones anormales
# mediante superposición de funciones sinusoidales y ruido

def simulate_misalignment(duration=1.0, fs=12000):
    """Simula vibración por desalineamiento de guía."""
    t = np.arange(0, duration, 1/fs)
    # Oscilación amortiguada a frecuencia dominante ~20 Hz
    signal = np.exp(-0.5*t) * np.sin(2*np.pi*20*t)
    signal += 0.1 * np.random.randn(len(signal))
    return signal
```

## Estructura de datos en notebook

Ambas fuentes se procesan a un formato uniforme:
- **Entrada**: Señal 1D de aceleración (4096 muestras, 12 kHz = ~0.34 segundos)
- **Salida**: Espectrograma RGB 224×224×3 (3 canales de componentes CWT)
- **Etiqueta**: Una de 4 clases: {Normal, Desalineamiento, Pandeo, Escalones}

**Ratio Entrenamiento/Validación**: 80% / 20%

## Reproducibilidad

Para reproducir exactamente los resultados:
1. Dataset CWRU: Se descarga desde URL oficial en el notebook
2. Datos sintéticos: Se generan con semilla fija (seed=42) para determinismo
3. Versiones pinned en `requirements.txt` garantizan reproducibilidad

**Nota**: El artículo original utiliza datos reales de ascensores (no públicos) provenientes de una compañía de elevadores (Abaqus CAE). Nuestros datos sintéticos son una aproximación representativa para fines educativos y de demostración.
