---
description: Vigila un artículo científico (link o PDF) y genera su expediente completo en articles/
---

Vas a dar de alta un artículo científico nuevo en este repo "vigía", siguiendo al pie de la letra
`CONSTITUTION.md`. El artículo (link o ruta a PDF local) es:

$ARGUMENTS

Si no se ha proporcionado ningún argumento, pide al usuario el link o la ruta al PDF antes de
continuar.

Ejecuta las fases en orden. **Ante cualquier ambigüedad o decisión que no puedas resolver con
confianza, usa `AskUserQuestion` y espera la respuesta antes de continuar** — no asumas.

## Fase 0 — Preparación

1. Lee `CONSTITUTION.md` y `taxonomy.yaml` si no los tienes ya en contexto.
2. Obtén el contenido del artículo:
   - Si es una URL, usa `WebFetch`.
   - Si es una ruta local a un PDF, usa `Read` (puedes leer PDFs directamente).
3. Deriva un `slug` en kebab-case, corto y estable (p.ej. `2026-08-02-nombre-del-articulo`), y
   crea `articles/<slug>/` copiando la estructura de `articles/_template/` como punto de partida
   (no reutilices el contenido de ejemplo, solo la estructura). Este `slug` será también la clave
   de citación en `references.bib`.
4. **Recuerda: nunca copies ni guardes el PDF/texto completo del artículo en el repo.** Solo su
   `source_url`/DOI en `metadata.yaml`.
5. Rellena en `metadata.yaml` los campos bibliográficos: `entry_type` (`article` /
   `inproceedings` / `techreport` / `misc`), `year`, y si existen, `venue` (revista/conferencia) y
   `doi`. Si no tienes claro el `entry_type` correcto, pregunta al usuario en vez de adivinar.

## Fase 1 — Resumen

Genera `summary.md`: objetivo, método, resultados principales y limitaciones, en un lenguaje claro
e informativo (no una traducción literal del abstract).

## Fase 2 — Clasificación por keywords

1. Carga `taxonomy.yaml` y elige las keywords existentes que mejor describan la temática del
   artículo (puede ser más de una).
2. Si **ninguna** encaja razonablemente, propón una keyword nueva (nombre + descripción breve) y
   **pide confirmación explícita al usuario con `AskUserQuestion`** antes de añadirla a
   `taxonomy.yaml`. No la añadas si el usuario prefiere reutilizar una existente aunque encaje
   peor.
3. Escribe las keywords finales en `metadata.yaml` del artículo.

## Fase 3 — Código de reuso

1. Evalúa si es viable implementar en Python (u otro lenguaje open source, justificando la
   elección si no es Python) una versión reutilizable de la técnica/algoritmo del artículo.
2. Si es viable: impleméntala en `src/`, usando únicamente librerías open source (nada que
   requiera una API de pago para poder ejecutarse).
3. Si **no** es viable (p.ej. artículo puramente teórico/de revisión sin algoritmo implementable),
   no fuerces código de relleno: documenta el motivo en `NOT_FEASIBLE.md` y elimina `src/`,
   `tests/` y `requirements.txt` de la copia de la plantilla. Si tienes dudas sobre si es viable o
   no, pregunta al usuario antes de decidir.

## Fase 4 — Datos reproducibles

1. Busca datasets públicos reales que permitan reproducir los resultados del artículo (el propio
   paper, repositorios de datasets, código complementario de los autores, etc.).
2. Si encuentras uno adecuado, documenta en `data/README.md` su fuente, licencia y cómo se carga.
3. Si no existe o no es accesible, genera datos sintéticos representativos y documenta en
   `data/README.md` cómo se generan y por qué son representativos del fenómeno del artículo. Si
   no tienes claro qué debería representar el dataset sintético, pregunta al usuario.

## Fase 5 — Notebook de reproducción

Genera `notebook.ipynb` que cargue los datos (públicos o sintéticos), ejecute el código de `src/`
y visualice los resultados clave (gráficas comparables a las del artículo cuando sea posible). El
notebook debe poder ejecutarse de principio a fin sin errores.

## Fase 6 — Calidad y verificación

1. Si existe `src/`: escribe tests en `tests/` con el objetivo de **100% de cobertura**, y
   `requirements.txt` con las dependencias ancladas a una versión concreta.
2. Ejecuta:
   ```bash
   python scripts/validate_article.py articles/<slug>
   ```
3. Corrige cualquier fallo (lint, cobertura, notebook, metadata, keywords) hasta que el script
   termine sin errores. No des el artículo por terminado si el script falla.
4. Regenera la bibliografía y comprueba que queda al día:
   ```bash
   python scripts/generate_bibliography.py
   ```
   El nuevo artículo debe aparecer en `references.bib` con clave `<slug>`. Si no aparece, revisa
   que `metadata.yaml` tenga `entry_type`, `title`, `authors`, `year` y `source_url`.

## Cierre

1. Enséñale al usuario un resumen del expediente creado (fases completadas, keywords asignadas,
   si se generó código o `NOT_FEASIBLE.md`, origen de los datos).
2. Actualiza `articles/README.md` añadiendo la fila correspondiente (y agrupación por keyword).
3. **Pregunta al usuario si quiere que hagas commit / push** de los cambios (y, en su caso, que
   abras un PR). No lo hagas de forma automática sin esa confirmación explícita.
