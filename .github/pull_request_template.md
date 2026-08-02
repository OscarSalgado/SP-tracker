## Descripción

<!-- Qué artículo(s) se añaden o modifican y un resumen breve. -->

## Checklist (ver CONSTITUTION.md)

- [ ] No se ha commiteado el PDF ni el texto completo del artículo original.
- [ ] `metadata.yaml` completo (título, autores, `source_url`/DOI, fecha, `keywords`, `status`,
      `data_source`).
- [ ] Las `keywords` existen en `taxonomy.yaml` (si se añade una nueva, incluida en este PR con su
      descripción y confirmada por una persona).
- [ ] `summary.md` presente.
- [ ] `src/` con código de reuso open source, **o** `NOT_FEASIBLE.md` justificando por qué no es
      viable.
- [ ] Si existe `src/`: `tests/` con 100% de cobertura y `requirements.txt` anclado.
- [ ] `data/README.md` documentando el origen de los datos (público o sintético).
- [ ] `notebook.ipynb` ejecuta de principio a fin sin errores.
- [ ] `python scripts/validate_article.py articles/<slug>` pasa sin errores.
