# Configuración de protección de rama para SP-tracker

Este documento describe la configuración necesaria en GitHub para hacer cumplir los estándares de calidad del repositorio a través de checks automáticos.

## Estado actual

- ✅ El workflow CI (`article-pr-checks.yml`) está configurado y ejecuta automáticamente todos los checks
- ✅ El job `gate` agrega todos los resultados bajo un único nombre de check estable
- ⚠️ **Falta**: Configurar el job `gate` como "required status check" en la rama `main`

## Qué necesita hacerse

El job `gate` del workflow de CI debe marcarse como **"required status check"** en la protección de rama de GitHub. Esto garantiza que ningún PR pueda mergearse si falla alguno de los controles de calidad.

## Pasos para configurar (requiere permisos de admin del repo)

1. Ve a **Settings** de tu repositorio en GitHub
2. Haz clic en **Branches** en el menú lateral izquierdo
3. Bajo "Branch protection rules", busca la regla para `main` (o crea una si no existe)
4. En la sección **"Require status checks to pass before merging"**:
   - Marca la casilla para habilitarlo
   - Busca y selecciona el check llamado **`gate`**
   - Verifica que también estén seleccionados otros checks importantes (p.ej., si hay otros workflows)
5. Opcionalmente, habilita también:
   - **"Require branches to be up to date before merging"** (recomendado)
   - **"Dismiss stale pull request approvals when new commits are pushed"** (recomendado)
   - **"Require code reviews before merging"** (depende de tu política)
6. Haz clic en **"Save changes"**

## Resultado esperado después de configurar

Una vez que el check `gate` esté marcado como "required":

- Los PRs que modifiquen `articles/**` no podrán mergearse hasta que `gate` sea verde (success)
- Si algún artículo no cumple con los estándares de CONSTITUTION.md, el `gate` fallará
- Los desarrolladores verán claramente qué está fallando en el PR y podrán corregir antes de mergear

## Checks que incluye `gate`

El job `gate` verifica que todos estos pasos tengan éxito:

1. **ruff check**: Linting del código (`src/` y `tests/`)
2. **ruff format --check**: Formato consistente del código
3. **pytest --cov=src --cov-fail-under=100**: Tests con 100% de cobertura
4. **python scripts/validate_article.py**: Validación según CONSTITUTION.md
5. **python scripts/generate_bibliography.py --check**: references.bib está actualizado

Si el PR modifica `taxonomy.yaml` o `scripts/validate_article.py`, todos los artículos existentes se revalidan (no solo los del diff).

## Más información

- Ver [CONSTITUTION.md](../CONSTITUTION.md) para los estándares completos
- Ver [article-pr-checks.yml](workflows/article-pr-checks.yml) para el workflow de CI
