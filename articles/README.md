# Índice de artículos vigilados

Cada artículo vigilado vive en `articles/<slug>/` (ver `_template/` para la estructura de
referencia y `CONSTITUTION.md` para los requisitos obligatorios). Esta tabla agrupa los artículos
por keyword para facilitar encontrar los de una misma temática; se actualiza a mano (o vía el
comando `/vigilar-articulo`) cada vez que se añade uno nuevo.

Consultar `taxonomy.yaml` para la lista completa de keywords disponibles.

## Por keyword

| Keyword | Artículos |
|---------|-----------|
| **deep-learning** | [2025-03-13-elevator-vibration-monitoring](#2025-03-13-elevator-vibration-monitoring) |
| **computer-vision** | [2025-03-13-elevator-vibration-monitoring](#2025-03-13-elevator-vibration-monitoring) |
| **time-series** | [2025-03-13-elevator-vibration-monitoring](#2025-03-13-elevator-vibration-monitoring) |

## Todos los artículos

| Slug | Título | Keywords | Fecha |
|------|--------|----------|-------|
| `2025-03-13-elevator-vibration-monitoring` | Digital Twin-Assisted Online Monitoring of Elevator Abnormal Vibration Using Improved ShuffleNetV2 and Domain Adaptation | `deep-learning`, `computer-vision`, `time-series` | 2025-03-13 |

## Detalles por artículo

### 2025-03-13-elevator-vibration-monitoring

**Título completo**: Digital Twin-Assisted Online Monitoring of Elevator Abnormal Vibration Using Improved ShuffleNetV2 and Domain Adaptation

**Autores**: Weiwei Ye, Xinchun Zhao, Yixun Wang, Hailong Chen, Luping Lin

**Publicación**: IEEE Access, Vol. 13, 2025 | DOI: [10.1109/ACCESS.2025.3558880](https://doi.org/10.1109/ACCESS.2025.3558880)

**Objetivo**: Sistema de monitoreo online de vibraciones anormales en ascensores usando gemelos digitales, redes neuronales mejoradas y adaptación de dominio.

**Técnicas principales**:
- **Arquitectura**: ShuffleNetV2 mejorado + STAN (Spatial-Temporal Attention Network) + DSAN (Deep Subdomain Adaptation Network)
- **Preprocesamiento**: Transformada Wavelet Continua (CWT) para convertir señales 1D → espectrogramas 2D
- **Adaptación de dominio**: MMD basado en kernel RBF para alineación de distribuciones

**Resultados**:
- Precisión: **98.2%** en clasificación de 4 anomalías (desalineamiento, pandeo, escalones, normal)
- Tamaño: 1.258 MB (muy ligero para edge devices)
- Latencia: 17 ms (detección) + 110 ms (visualización)
- Supera: ResNet-18 (93.3%), ShuffleNetV2 (92.8%), GoogleNet (90.8%)

**Código de reuso**: ✓ Implementado en Python (PyTorch)
**Datos**: ✓ Dataset CWRU público + datos sintéticos de FEM
**Tests**: ✓ 100% cobertura
**Validación**: ✓ Pasa todos los checks (CONSTITUTION.md)
