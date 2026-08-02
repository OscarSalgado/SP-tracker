# Constitución del repo SP-tracker

Este documento fija los estándares **obligatorios** para cualquier Pull Request que añada o
modifique un artículo vigilado en `articles/**`. Los PRs que no los cumplan no deben mergearse.
La comprobación automática de estas reglas vive en `scripts/validate_article.py`, que es la
**fuente de verdad ejecutable**: si este documento y el script alguna vez difieren, gana el
script y hay que corregir el documento.

## 1. Qué es un "artículo vigilado"

Un artículo vigilado es un directorio `articles/<slug>/` con la misma estructura que
`articles/_template/`. `<slug>` es un identificador corto y estable (kebab-case), por ejemplo
`2026-08-02-attention-is-all-you-need`.

## 2. Prohibido: commitear el material original con copyright

- **No se sube el PDF ni el texto completo del artículo** al repositorio, bajo ningún concepto.
- Solo se referencia el artículo original mediante su `source_url` y/o DOI en `metadata.yaml`.
- Todo el resto de contenido (resumen, código, datos, notebook) es contenido **derivado**,
  generado a partir del artículo, no una copia del mismo.

## 3. Contenido obligatorio de cada artículo

| Fichero/carpeta        | Obligatorio | Descripción |
|-------------------------|:-----------:|-------------|
| `metadata.yaml`          | Sí | Título, autores, `source_url`/DOI, fecha de vigilancia, `keywords` (deben existir en `taxonomy.yaml`), `status`, `data_source`. |
| `summary.md`             | Sí | Resumen informativo: objetivo, método, resultados principales, limitaciones. |
| `src/`                   | Sí* | Código (Python u otro lenguaje open source) que reproduce/reutiliza la técnica del artículo. |
| `NOT_FEASIBLE.md`        | Solo si no hay `src/` | Justificación razonada de por qué no es viable generar código de reuso. |
| `tests/`                 | Sí (si existe `src/`) | Tests con **100% de cobertura** sobre `src/`. |
| `data/README.md`         | Sí | Procedencia de los datos: dataset público (con fuente/licencia) o datos sintéticos (con script y justificación de representatividad). |
| `notebook.ipynb`         | Sí | Notebook que carga los datos, ejecuta el código y visualiza los resultados clave. Debe ejecutar de principio a fin sin errores. |
| `requirements.txt`       | Sí (si existe `src/`) | Dependencias ancladas a una versión concreta. Solo librerías open source; nada que exija una API de pago para reproducir el resultado. |

\* `src/` es obligatorio salvo que generar código de reuso sea realmente inviable (por ejemplo,
un artículo puramente teórico/de revisión sin algoritmo implementable). En ese caso, el
`NOT_FEASIBLE.md` sustituye a `src/`, `tests/` y `requirements.txt`, pero `summary.md`,
`data/README.md` (puede indicar "no aplica") y `notebook.ipynb` (puede reducirse a la
exploración/visualización del resumen) se mantienen.

## 4. Calidad de código

- `ruff check` y `ruff format --check` deben pasar sin errores sobre `src/` y `tests/`.
- Cobertura de tests: **100%** sobre `src/`, medida con `pytest --cov=src --cov-fail-under=100`.
- No se permite silenciar cobertura o lint con excepciones globales (`# pragma: no cover`,
  `# noqa` a nivel de fichero) salvo justificación puntual línea a línea.
- `notebook.ipynb` debe poder ejecutarse con `jupyter nbconvert --execute` sin lanzar excepciones.

## 5. Keywords y taxonomía

- Las `keywords` de `metadata.yaml` deben existir en `taxonomy.yaml`.
- Si ninguna keyword existente encaja con la temática del artículo, se puede añadir una nueva,
  pero **requiere confirmación humana explícita** y debe añadirse a `taxonomy.yaml` en el mismo
  PR, con una `description` breve.
- No se crean keywords duplicadas o sinónimas de una ya existente: se reutiliza la existente.

## 6. Verificación

Antes de abrir un PR (o de darlo por terminado en el propio comando `/vigilar-articulo`), debe
ejecutarse:

```bash
python scripts/validate_article.py articles/<slug>
```

La CI (`.github/workflows/article-pr-checks.yml`) ejecuta este mismo script sobre cada carpeta de
`articles/` que cambie en el PR, y el PR no debería mergearse si falla.

## 7. Automatización de referencia

El comando `/vigilar-articulo <url-o-ruta-pdf>` (definido en
`.claude/commands/vigilar-articulo.md`) implementa el flujo completo descrito en este documento.
Cualquier generación manual de un artículo debe seguir el mismo proceso y los mismos estándares.
