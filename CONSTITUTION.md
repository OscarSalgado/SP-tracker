# Constitución del repo SP-tracker

Estándares **obligatorios** para PRs sobre `articles/**`. La comprobación automática vive en
`scripts/validate_article.py`, que es la **fuente de verdad ejecutable**: si difiere del presente
documento, gana el script.

## 1. Estructura de un artículo vigilado

Un artículo vigilado es `articles/<slug>/` (slug: kebab-case, ej. `2026-08-02-attention-is-all-you-need`) con la estructura de `articles/_template/`.

## 2. Contenido obligatorio

No se commiteará el PDF ni texto original. Se referencia por `source_url`/DOI en `metadata.yaml`. El resto (resumen, código, datos, notebook) es derivado.

| Fichero | Obligatorio | Descripción |
|---------|:-----------:|-------------|
| `metadata.yaml` | Sí | Título, autores, `source_url`/DOI, keywords (de `taxonomy.yaml`), `status`, `data_source`, `entry_type`, `year`, `venue`/`doi` (sección 6). |
| `summary.md` | Sí | Objetivo, método, resultados, limitaciones. |
| `src/` | Sí* | Código open source que reproduce la técnica. |
| `NOT_FEASIBLE.md` | Si no hay `src/` | Justificación de inviabilidad. |
| `tests/` | Si hay `src/` | **100% cobertura** sobre `src/`. |
| `data/README.md` | Sí | Dataset público o datos sintéticos con justificación. |
| `notebook.ipynb` | Sí | Carga datos, ejecuta código, visualiza resultados. |
| `requirements.txt` | Si hay `src/` | Dependencias ancladas. Solo open source. |

\* Excepto artículos teóricos sin algoritmo implementable, que usan `NOT_FEASIBLE.md` en lugar de `src/`, `tests/`, `requirements.txt`.

## 3. Calidad de código

- `ruff check` y `ruff format --check` sin errores.
- **100% cobertura** de tests: `pytest --cov=src --cov-fail-under=100`.
- Sin excepciones globales (`# pragma: no cover`, `# noqa` globales). Solo puntualmente si se justifica.
- `notebook.ipynb` ejecutable sin excepciones (validado automáticamente).

## 4. Keywords y validación

Keywords en `metadata.yaml` deben existir en `taxonomy.yaml`. Nuevas keywords requieren confirmación explícita y deben añadirse a `taxonomy.yaml` en el mismo PR (sin duplicados/sinónimos).

Validar antes de abrir PR: `python scripts/validate_article.py articles/<slug>`.

La CI (`.github/workflows/article-pr-checks.yml`) ejecuta automáticamente. Si se toca `taxonomy.yaml` o `validate_article.py`, revalida todos los artículos. El job `gate` es el status check requerido.

## 5. Referencias BibTeX (`references.bib`)

`references.bib` es generado (nunca editado a mano) por `python scripts/generate_bibliography.py` a partir de `metadata.yaml`. La clave de citación es el `slug` del artículo.

Campos requeridos en `metadata.yaml`: `entry_type` (article|inproceedings|techreport|misc), `year`, `venue` (opt.), `doi` (opt.). Template excluido. La CI verifica actualización con `--check`.

## 6. Automatización

El comando `/vigilar-articulo <url-o-ruta-pdf>` implementa el flujo completo. Génesis manual debe seguir los mismos estándares.
