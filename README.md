# SP-tracker

Repositorio "vigía" de artículos científicos: cada artículo introducido (por link o PDF) se
convierte en un expediente reproducible con resumen, clasificación temática, código de reuso,
datos y un notebook — todo bajo controles de calidad estrictos.

## Cómo funciona

1. Se introduce un artículo (URL o PDF local).
2. Se genera un **resumen informativo**.
3. Se clasifica por **keywords** de un vocabulario controlado (`taxonomy.yaml`), para poder
   agrupar fácilmente artículos de la misma temática.
4. Si es viable, se genera **código Python (u open source)** que permite reutilizar la técnica.
5. Se localizan **datos públicos** que reproduzcan los resultados, o se generan **datos
   sintéticos** representativos si no existen.
6. Se genera un **Jupyter Notebook** que reproduce y visualiza los resultados.
7. Se registra en un **gestor de referencias bibliográficas** (`references.bib`, BibTeX).
8. Todo el código generado mantiene **controles estrictos de calidad**: tests con 100% de
   cobertura, dependencias ancladas, linting.

Las reglas obligatorias de este proceso están fijadas en [`CONSTITUTION.md`](CONSTITUTION.md);
cualquier Pull Request sobre `articles/**` debe cumplirlas (verificado en CI).

## Uso

Vigilar un artículo nuevo con Claude Code:

```
/vigilar-articulo <url-del-artículo-o-ruta-a-pdf-local>
```

El comando (definido en [`.claude/commands/vigilar-articulo.md`](.claude/commands/vigilar-articulo.md))
orquesta todas las fases anteriores y pide confirmación ante cualquier ambigüedad (nueva keyword,
viabilidad del código, ausencia de datos públicos, etc.).

Para validar manualmente un artículo ya creado:

```bash
pip install -r requirements-dev.txt
python scripts/validate_article.py articles/<slug>
```

Para regenerar el gestor de referencias bibliográficas (`references.bib`) a partir de los
`metadata.yaml` de todos los artículos:

```bash
python scripts/generate_bibliography.py          # regenera references.bib
python scripts/generate_bibliography.py --check  # falla si está desactualizado (usado en CI)
```

## Estructura

```
articles/
  README.md          # índice de artículos agrupados por keyword
  _template/         # plantilla de referencia (estructura mínima válida)
  <slug>/             # un directorio por artículo vigilado
    metadata.yaml
    summary.md
    src/               # código de reuso (o NOT_FEASIBLE.md si no es viable)
    tests/
    data/README.md
    notebook.ipynb
    requirements.txt
taxonomy.yaml         # vocabulario controlado de keywords
references.bib        # gestor de referencias bibliográficas (BibTeX, generado, no editar a mano)
CONSTITUTION.md       # estándares obligatorios para cualquier PR
scripts/validate_article.py       # validación automática (usada por CI y por el comando)
scripts/generate_bibliography.py  # genera/comprueba references.bib
```

Ver [`CONSTITUTION.md`](CONSTITUTION.md) para el detalle normativo completo y
[`articles/README.md`](articles/README.md) para el índice de artículos vigilados.
