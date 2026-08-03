"""Helper module para sugerir keywords en artículos.

Diseñado para integración en flujos automatizados como /vigilar-articulo.
"""

from __future__ import annotations

from pathlib import Path

from keyword_suggester import (
    load_current_keywords,
    load_summary,
    load_taxonomy,
    score_keywords,
)


def get_keyword_suggestions(
    article_dir: Path, threshold: float = 0.05, num_suggestions: int = 3
) -> list[str]:
    """Obtiene sugerencias de keywords para un artículo.

    Args:
        article_dir: Ruta al directorio articles/<slug>
        threshold: Puntuación mínima para incluir una sugerencia
        num_suggestions: Número máximo de sugerencias a retornar

    Returns:
        Lista de keywords sugeridas (ordenadas por puntuación descendente)
    """
    article_dir = Path(article_dir).resolve()

    summary = load_summary(article_dir)
    if not summary:
        return []

    current_keywords = load_current_keywords(article_dir)
    keywords_dict = load_taxonomy()

    scores = score_keywords(summary, keywords_dict, current_keywords)

    # Filtrar y ordenar
    suggestions = sorted(
        [(kw, score) for kw, score in scores.items() if score >= threshold],
        key=lambda x: x[1],
        reverse=True,
    )

    # Retornar solo los nombres, limitado a num_suggestions
    return [kw for kw, _ in suggestions[:num_suggestions]]


def format_suggestions_for_display(
    article_dir: Path, suggestions: list[str], current_keywords: list[str] | None = None
) -> str:
    """Formatea sugerencias para mostrar al usuario durante /vigilar-articulo.

    Args:
        article_dir: Ruta al directorio del artículo
        suggestions: Lista de keywords sugeridas
        current_keywords: Keywords actuales (si no se pasan, se cargan)

    Returns:
        String formateado para mostrar al usuario
    """
    if current_keywords is None:
        current_keywords = load_current_keywords(article_dir)

    if not suggestions and not current_keywords:
        return "⚠ No hay keywords sugeridas ni asignadas"

    output = []

    if current_keywords:
        output.append(f"✓ Keywords asignadas: {', '.join(current_keywords)}")

    if suggestions:
        output.append("\n💡 Keywords sugeridas adicionales:\n")
        for i, kw in enumerate(suggestions, 1):
            output.append(f"  {i}. {kw}")

    return "\n".join(output)
