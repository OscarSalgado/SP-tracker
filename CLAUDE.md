# CLAUDE.md

Instrucciones de proyecto para cualquier sesión de Claude Code que trabaje en este repositorio.

## Qué es este repo

`SP-tracker` es un repositorio "vigía" de artículos científicos. Cada artículo introducido (por
link o PDF) se convierte en un expediente en `articles/<slug>/` con: resumen, clasificación por
keywords, código de reuso (cuando es viable), datos reproducibles (públicos o sintéticos) y un
notebook de reproducción/visualización — todo bajo los controles de calidad fijados en
`CONSTITUTION.md`.

## Fuente de verdad normativa

**`CONSTITUTION.md` es obligatoria.** Cualquier PR que toque `articles/**` debe cumplirla. Antes
de proponer o aceptar cambios en la estructura de un artículo, léela. La comprobación automática
de sus reglas está en `scripts/validate_article.py`.

## Cómo se vigila un artículo nuevo

Usar el comando `/vigilar-articulo <url-o-ruta-pdf>` (`.claude/commands/vigilar-articulo.md`).
Orquesta las fases: resumen → clasificación por keywords (`taxonomy.yaml`) → código de reuso →
datos (públicos o sintéticos) → notebook → verificación de calidad. El comando debe pedir
confirmación al usuario ante cualquier ambigüedad (nueva keyword, viabilidad del código, ausencia
de datos públicos, etc.) en vez de asumir.

## Reglas clave a recordar

- **Nunca commitear el PDF ni el texto completo de un artículo** (copyright). Solo se referencia
  por `source_url`/DOI.
- Las keywords deben salir de `taxonomy.yaml`; una keyword nueva requiere confirmación humana y se
  añade en el mismo PR.
- El código de reuso debe usar únicamente librerías open source.
- `src/` requiere 100% de cobertura de tests si existe.
- No abrir un PR ni hacer push sin confirmación explícita del usuario, siguiendo las reglas
  generales de la sesión sobre acciones que afectan estado compartido.
