#!/usr/bin/env python3
"""Extrae el contenido esencial de un PDF, reduciendo tokens.

Carga solo: título, autores, abstract, intro, métodos, resultados, conclusiones.
Omite: referencias, apéndices, portadas extras, tablas de contenidos.

Uso:
    python scripts/extract_pdf_essence.py <ruta-pdf>

Retorna texto limpio para pasar a Claude, típicamente 30-50% del PDF original.
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    print("Error: instala pdfplumber: pip install pdfplumber", file=sys.stderr)
    sys.exit(1)


KEYWORDS_START = {
    "abstract", "resumen", "introduction", "introducción",
    "introduction and related work", "method", "metodología", "methodology",
    "approach", "algorithm", "sistema", "system", "background"
}

KEYWORDS_END = {
    "references", "bibliography", "bibliografía", "appendix", "apéndice",
    "supplementary", "suplementario", "acknowledgment", "agradecimientos",
    "author contributions", "contributions", "data availability"
}

PAGES_LIMIT = 20  # Máximo de páginas a procesar (típicamente 1-20 contienen lo esencial)


def extract_pdf_text(pdf_path: str | Path) -> str:
    """Extrae texto esencial del PDF, omitiendo referencias y apéndices."""
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"{pdf_path} no existe")

    texts = []
    found_main_content = False

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages[:PAGES_LIMIT]):
                text = page.extract_text() or ""
                if not text.strip():
                    continue

                lower_text = text.lower()

                # Detectar inicio de contenido principal
                if any(kw in lower_text for kw in KEYWORDS_START):
                    found_main_content = True

                # Detectar fin (referencias, apéndices)
                if any(kw in lower_text for kw in KEYWORDS_END):
                    break

                # Solo incluir si ya encontramos contenido o esta página lo tiene
                if found_main_content or any(kw in lower_text for kw in KEYWORDS_START):
                    texts.append(text)

    except Exception as e:
        raise RuntimeError(f"Error leyendo PDF: {e}")

    return "\n\n".join(texts)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 1

    pdf_path = sys.argv[1]
    try:
        content = extract_pdf_text(pdf_path)
        print(content)
        return 0
    except (FileNotFoundError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
