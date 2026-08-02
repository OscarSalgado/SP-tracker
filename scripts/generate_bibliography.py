#!/usr/bin/env python3
"""Genera references.bib a partir de los metadata.yaml de cada articles/<slug>/.

references.bib es contenido derivado: no se edita a mano (ver CONSTITUTION.md sección 7).
Este script es la única fuente que lo escribe; la CI comprueba con --check que está
actualizado.

    python scripts/generate_bibliography.py          # regenera references.bib
    python scripts/generate_bibliography.py --check  # falla si está desactualizado
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTICLES_DIR = REPO_ROOT / "articles"
BIBLIOGRAPHY_PATH = REPO_ROOT / "references.bib"

REQUIRED_BIB_FIELDS = ("entry_type", "title", "authors", "year", "source_url")
VENUE_FIELD_BY_ENTRY_TYPE = {
    "article": "journal",
    "inproceedings": "booktitle",
    "techreport": "institution",
}

HEADER = (
    "% references.bib -- generado automáticamente por scripts/generate_bibliography.py\n"
    "% No editar a mano: los cambios se sobreescriben. Editar el metadata.yaml del\n"
    "% artículo correspondiente y volver a ejecutar el script.\n\n"
)


def _escape(value: str) -> str:
    return value.replace("{", "\\{").replace("}", "\\}")


def _field(name: str, value: str) -> str:
    return f"  {name} = {{{_escape(value)}}},"


def build_entry(slug: str, metadata: dict) -> str:
    lines = [f"@{metadata['entry_type']}{{{slug},"]
    lines.append(_field("title", metadata["title"]))
    lines.append(_field("author", " and ".join(metadata["authors"])))
    lines.append(_field("year", str(metadata["year"])))

    if metadata.get("venue"):
        venue_field = VENUE_FIELD_BY_ENTRY_TYPE.get(metadata["entry_type"], "note")
        lines.append(_field(venue_field, metadata["venue"]))

    if metadata.get("doi"):
        lines.append(_field("doi", metadata["doi"]))

    lines.append(_field("url", metadata["source_url"]))

    if metadata.get("keywords"):
        lines.append(_field("keywords", ", ".join(metadata["keywords"])))

    lines.append("}")
    return "\n".join(lines)


def collect_entries() -> list[str]:
    entries = []
    for article_dir in sorted(ARTICLES_DIR.iterdir()):
        if not article_dir.is_dir() or article_dir.name.startswith("_"):
            continue

        metadata_path = article_dir / "metadata.yaml"
        if not metadata_path.is_file():
            continue

        metadata = yaml.safe_load(metadata_path.read_text()) or {}
        missing = [key for key in REQUIRED_BIB_FIELDS if not metadata.get(key)]
        if missing:
            print(
                f"aviso: {article_dir.name} no tiene {', '.join(missing)} en metadata.yaml, "
                "se omite de references.bib",
                file=sys.stderr,
            )
            continue

        entries.append(build_entry(article_dir.name, metadata))

    return entries


def render_bibliography(entries: list[str]) -> str:
    if not entries:
        return HEADER
    return HEADER + "\n\n".join(entries) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="No escribir el fichero: fallar si references.bib está desactualizado",
    )
    args = parser.parse_args()

    entries = collect_entries()
    content = render_bibliography(entries)

    if args.check:
        current = BIBLIOGRAPHY_PATH.read_text() if BIBLIOGRAPHY_PATH.is_file() else None
        if current != content:
            print(
                "references.bib está desactualizado. Ejecuta "
                "`python scripts/generate_bibliography.py` y commitea el resultado.",
                file=sys.stderr,
            )
            return 1
        print("references.bib está actualizado.")
        return 0

    BIBLIOGRAPHY_PATH.write_text(content)
    print(f"references.bib actualizado ({len(entries)} entradas).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
