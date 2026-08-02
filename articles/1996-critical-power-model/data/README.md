# Datos

## Procedencia

Los datos originales del artículo de Morton (1996) fueron tomados del estudio de **McLellan y Cheung (1992)**, que incluía 14 sujetos entrenados realizando pruebas de cicloergometría a diferentes potencias hasta exhaustación.

**Los datos originales no están disponibles públicamente** (acceso restringido / datos históricos). Por lo tanto, se han generado **datos sintéticos representativos** que capturan la estructura y el comportamiento reportados en el artículo.

## Generación de datos sintéticos

Los datos sintéticos se generan en el notebook `notebook.ipynb` usando el modelo 3-parámetros calibrado con valores típicos de los sujetos del estudio de Morton:

```python
# Parámetros representativos (basados en Tabla 2 de Morton 1996, promedio de sujetos)
AWC_mean = 24000  # joules
CP_mean = 252     # watts
k_mean = -20      # segundos (promedio de valores negativos)

# Se generan 12 sujetos sintéticos con variabilidad
```

### Por qué son representativos

1. **Rango de valores**: AWC ∈ [12,000–130,000 J], CP ∈ [82–308 W], k ∈ [-534, -3] s, capturan la diversidad observada en Tabla 2.
2. **Modelo subyacente**: Los tiempos se generan usando (P - CP) · (t - k) = AWC + ruido gaussiano (~5s), reflejando la incertidumbre de medición.
3. **Spread de potencia**: Se usan 5 potencias por sujeto (baja, media-baja, media, media-alta, alta), como recomienda Morton.

## Uso en análisis

El notebook carga estos datos, ajusta ambos modelos (2-param y 3-param), y reproduce los resultados clave del artículo:
- El modelo 3-param produce menores RMS que el 2-param
- Estimaciones de AWC son mayores y de CP menores con 3-param
- Se visualiza el parámetro P_max para cada sujeto

## Validación futura

Para reproducir resultados con datos reales, contactar a autores del estudio original o buscar repositorios de datos de investigación (e.g., Zenodo, DRYAD) si se publica en futuros trabajos.
