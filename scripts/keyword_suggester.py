#!/usr/bin/env python3
"""Sugiere keywords relevantes para un artículo basándose en su summary.md.

Uso:
    python scripts/keyword_suggester.py articles/<slug>
    python scripts/keyword_suggester.py articles/<slug> --show-scores

El script analiza términos frecuentes en summary.md y compara con la
taxonomía para sugerir keywords no asignadas pero potencialmente relevantes.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
TAXONOMY_PATH = REPO_ROOT / "taxonomy.yaml"

# Palabras clave asociadas a cada keyword en taxonomy.yaml.
# Se usan para detectar qué keywords son relevantes al analizar el summary.
KEYWORD_TERMS = {
    "machine-learning": {
        "terms": {
            "machine learning", "aprendizaje automático", "supervised learning",
            "unsupervised learning", "training", "model", "algoritmo", "clasificación",
            "clustering", "regression", "feature", "datos etiquetados", "predictor"
        }
    },
    "deep-learning": {
        "terms": {
            "deep learning", "redes neuronales", "neural network", "cnn", "rnn",
            "lstm", "transformer", "convolutional", "arquitectura", "capas",
            "backpropagation", "entrenamiento de redes", "activación"
        }
    },
    "nlp": {
        "terms": {
            "nlp", "procesamiento de lenguaje", "language model", "embeddings",
            "text classification", "generación de texto", "traducción automática",
            "tokenización", "bert", "gpt", "word2vec", "resumen de texto",
            "análisis de sentimiento"
        }
    },
    "computer-vision": {
        "terms": {
            "computer vision", "visión por computador", "image classification",
            "detección de objetos", "object detection", "segmentación de imágenes",
            "reconocimiento facial", "video analysis", "yolo", "cnn visual",
            "detección de bordes"
        }
    },
    "optimization": {
        "terms": {
            "optimization", "optimización", "algoritmo genético", "simulated annealing",
            "descenso de gradiente", "metaheurística", "particle swarm", "minimización",
            "maximización", "programación lineal", "búsqueda", "convergencia",
            "función objetivo", "runge-kutta"
        }
    },
    "time-series": {
        "terms": {
            "time series", "series temporal", "serie temporal", "temporal", "predicción",
            "forecasting", "detección de anomalías", "anomaly detection", "autocorrelación",
            "arima", "movimiento promedio", "tendencia", "estacionariedad", "análisis temporal",
            "retraso temporal"
        }
    },
    "vibration-analysis": {
        "terms": {
            "vibration", "vibración", "vibraciones", "análisis de vibración", "separación de componentes",
            "diagnóstico de maquinaria", "rotación", "rodamientos", "engranajes",
            "señal de vibración", "fallo en rodamiento", "bearing", "mecánica rotatoria",
            "frecuencia natural", "modos de vibración", "dinámica", "dinámico", "fft",
            "estress", "estrés", "aceleración", "amortiguamiento", "frecuencias", "transitorios",
            "impulsivos", "excentricidad", "oscilaciones"
        }
    }
}


def load_taxonomy() -> dict[str, dict]:
    """Carga taxonomy.yaml y enriquece con términos predefinidos."""
    data = yaml.safe_load(TAXONOMY_PATH.read_text()) or {}
    keywords_dict = {}
    for entry in data.get("keywords", []):
        name = entry["name"]
        keywords_dict[name] = {
            "description": entry.get("description", ""),
            "terms": KEYWORD_TERMS.get(name, {}).get("terms", set())
        }
    return keywords_dict


def load_summary(article_dir: Path) -> str:
    """Carga el contenido de summary.md."""
    summary_path = article_dir / "summary.md"
    if not summary_path.is_file():
        return ""
    return summary_path.read_text()


def load_current_keywords(article_dir: Path) -> list[str]:
    """Carga las keywords ya asignadas en metadata.yaml."""
    metadata_path = article_dir / "metadata.yaml"
    if not metadata_path.is_file():
        return []

    metadata = yaml.safe_load(metadata_path.read_text()) or {}
    keywords = metadata.get("keywords", [])
    return keywords if isinstance(keywords, list) else []


def normalize_text(text: str) -> str:
    """Normaliza texto: minúsculas, remove acentos, puntuación."""
    # Convertir a minúsculas
    text = text.lower()
    # Remover acentos simples
    text = text.replace("á", "a").replace("é", "e").replace("í", "i")
    text = text.replace("ó", "o").replace("ú", "u").replace("ñ", "n")
    return text


def score_keywords(summary: str, keywords_dict: dict[str, dict], current_keywords: list[str]) -> dict[str, float]:
    """Puntúa cada keyword basándose en frecuencia de términos en el summary."""
    if not summary:
        return {}

    normalized_summary = normalize_text(summary)
    scores = {}

    for keyword_name, keyword_info in keywords_dict.items():
        if keyword_name in current_keywords:
            # No sugerir keywords ya asignadas
            continue

        terms = keyword_info.get("terms", set())
        if not terms:
            scores[keyword_name] = 0.0
            continue

        # Contar matches de cada término en el summary
        matched_terms = set()
        for term in terms:
            normalized_term = normalize_text(term)
            # Buscar término: si tiene espacios, buscar como frase; si no, buscar palabra completa
            if " " in normalized_term:
                # Para frases: búsqueda substring simple
                if normalized_term in normalized_summary:
                    matched_terms.add(term)
            else:
                # Para palabras: usar word boundaries
                pattern = r"\b" + re.escape(normalized_term) + r"\b"
                if re.search(pattern, normalized_summary):
                    matched_terms.add(term)

        # Normalizar por cantidad de términos definidos
        # Usar un scoring que favorecer tener varios términos coincidentes
        num_matched = len(matched_terms)
        num_total = len(terms)
        scores[keyword_name] = (num_matched / num_total) if num_total > 0 else 0.0

    return scores


def suggest_keywords(
    article_dir: Path,
    threshold: float = 0.1,
    show_scores: bool = False
) -> dict:
    """Sugiere keywords para un artículo."""
    article_dir = article_dir.resolve()

    if not article_dir.is_dir():
        return {"error": f"{article_dir} no es un directorio"}

    summary = load_summary(article_dir)
    if not summary:
        return {"error": f"No se encontró summary.md en {article_dir}"}

    current_keywords = load_current_keywords(article_dir)
    keywords_dict = load_taxonomy()

    if not keywords_dict:
        return {"error": "No se pudo cargar taxonomy.yaml"}

    # Puntuar keywords
    scores = score_keywords(summary, keywords_dict, current_keywords)

    # Filtrar por threshold y ordenar por puntuación
    suggestions = {
        kw: score
        for kw, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)
        if score >= threshold
    }

    return {
        "article_dir": str(article_dir),
        "current_keywords": current_keywords,
        "suggestions": suggestions if show_scores else list(suggestions.keys()),
        "all_scores": scores if show_scores else None
    }


def format_output(result: dict, show_scores: bool = False) -> str:
    """Formatea el resultado para mostrar al usuario."""
    if "error" in result:
        return f"Error: {result['error']}"

    output = []
    article_dir = result["article_dir"]
    current = result["current_keywords"]
    suggestions = result["suggestions"]

    output.append(f"\n📍 Artículo: {article_dir}\n")

    if current:
        output.append(f"✓ Keywords actuales: {', '.join(current)}")
    else:
        output.append("⚠ Sin keywords asignadas")

    if show_scores and isinstance(suggestions, dict):
        if suggestions:
            output.append(f"\n💡 Keywords sugeridas (threshold ≥ 0.05):\n")
            for kw, score in suggestions.items():
                output.append(f"  • {kw:<30} (score: {score:.3f})")
        else:
            output.append("\n💡 Sin sugerencias (baja relevancia)")
    elif isinstance(suggestions, list):
        if suggestions:
            output.append(f"\n💡 Keywords sugeridas:\n")
            for kw in suggestions:
                output.append(f"  • {kw}")
        else:
            output.append("\n💡 Sin sugerencias (baja relevancia)")

    return "\n".join(output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "article",
        nargs="?",
        type=Path,
        help="Ruta a directorio articles/<slug>"
    )
    parser.add_argument(
        "--show-scores",
        action="store_true",
        help="Mostrar puntuaciones detalladas"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output como JSON (para integración programática)"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.05,
        help="Puntuación mínima para sugerir (default: 0.05)"
    )

    args = parser.parse_args()

    if not args.article:
        parser.print_help()
        return 1

    result = suggest_keywords(args.article, threshold=args.threshold, show_scores=args.show_scores)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_output(result, show_scores=args.show_scores))

    return 0 if "error" not in result else 1


if __name__ == "__main__":
    raise SystemExit(main())
