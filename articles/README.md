# Índice de artículos vigilados

Cada artículo vigilado vive en `articles/<slug>/` (ver `_template/` para la estructura de
referencia y `CONSTITUTION.md` para los requisitos obligatorios). Esta tabla agrupa los artículos
por keyword para facilitar encontrar los de una misma temática; se actualiza a mano (o vía el
comando `/vigilar-articulo`) cada vez que se añade uno nuevo.

Consultar `taxonomy.yaml` para la lista completa de keywords disponibles.

## Por keyword

| Keyword | Artículos |
|---------|-----------|
| vibration-analysis | [2026-08-05-blind-vibration-separation](#2026-08-05-blind-vibration-separation), [2026-08-05-classifier-guided-blind-deconvolution](#2026-08-05-classifier-guided-blind-deconvolution), [2026-08-05-kolmogorov-arnold-networks-fault-diagnosis](#2026-08-05-kolmogorov-arnold-networks-fault-diagnosis), [2026-08-05-realistic-evaluation-ml](#2026-08-05-realistic-evaluation-ml) |
| deep-learning | [2026-08-05-blind-vibration-separation](#2026-08-05-blind-vibration-separation), [2026-08-05-classifier-guided-blind-deconvolution](#2026-08-05-classifier-guided-blind-deconvolution), [2026-08-05-kolmogorov-arnold-networks-fault-diagnosis](#2026-08-05-kolmogorov-arnold-networks-fault-diagnosis) |
| signal-separation | [2026-08-05-blind-vibration-separation](#2026-08-05-blind-vibration-separation), [2026-08-05-classifier-guided-blind-deconvolution](#2026-08-05-classifier-guided-blind-deconvolution) |
| machine-learning | [2026-08-05-kolmogorov-arnold-networks-fault-diagnosis](#2026-08-05-kolmogorov-arnold-networks-fault-diagnosis), [2026-08-05-realistic-evaluation-ml](#2026-08-05-realistic-evaluation-ml) |

## Todos los artículos

| Slug | Título | Keywords | Fecha |
|------|--------|----------|-------|
| `2026-08-05-blind-vibration-separation` | Blind Separation of Vibration Sources using Deep Learning and Deconvolution | vibration-analysis, deep-learning, signal-separation | 2026-08-05 |
| `2026-08-05-classifier-guided-blind-deconvolution` | Classifier-guided neural blind deconvolution for bearing fault diagnosis under heavy noise | deep-learning, signal-separation, vibration-analysis | 2026-08-05 |
| `2026-08-05-kolmogorov-arnold-networks-fault-diagnosis` | Explainable fault and severity classification for rolling element bearings using Kolmogorov-Arnold networks | deep-learning, vibration-analysis, machine-learning | 2026-08-05 |
| `2026-08-05-realistic-evaluation-ml` | Realistic Evaluation of Machine Learning Models for Bearing Fault Diagnosis Under Industrial Conditions | machine-learning, vibration-analysis | 2026-08-05 |

---

### 2026-08-05-blind-vibration-separation

**ArXiv**: [2405.12774](https://arxiv.org/abs/2405.12774) | **Autores**: Makienko, Grebshtein, Gildish

Separación ciega de fuentes de vibración (engranaje + rodamiento) en maquinaria rotatoria usando CNN dilated y Whitening-Based Deconvolution. Código reproducible en PyTorch + datos sintéticos + notebook de demostración.

---

### 2026-08-05-classifier-guided-blind-deconvolution

**ArXiv**: [2404.15341](https://arxiv.org/abs/2404.15341) | **Autores**: Liao, He, Li, Sun, Zhang, Zhang

Diagnóstico de fallos en rodamientos bajo ruido severo usando deconvolución ciega neural guiada por clasificador. Implementación de Quadratic CNN + filtros neurales (temporal y frecuencial) + clasificador de 4 clases (sano, pista interna, pista externa, bola). Código PyTorch con tests al 100% y notebook de validación.

---

### 2026-08-05-kolmogorov-arnold-networks-fault-diagnosis

**ArXiv**: [2412.01322](https://arxiv.org/abs/2412.01322) | **Autores**: Rigas, Papachristou, Sotiropoulos, Alexandridis

Clasificación interpretable de fallos en rodamientos usando Redes Kolmogorov-Arnold (KAN). Implementa selección automática de características, hiperparámetros optimizables, y funciones de activación univariadas aprendibles. Clasificación de 5 clases (sano, pista interna, pista externa, bola, combinación) con énfasis en interpretabilidad.

---

### 2026-08-05-realistic-evaluation-ml

**ArXiv**: [2509.22267](https://arxiv.org/abs/2509.22267) | **Estado**: NOT_FEASIBLE

Evaluación realista de modelos ML para diagnóstico de fallos en rodamientos bajo condiciones industriales. Artículo marcado como no viable debido a restricciones de acceso durante la indexación. Requiere acceso manual al PDF/abstract para generar código de reuso.
