#!/usr/bin/env python3
"""Extrae contenido esencial de un PDF para Claude, reduciendo tokens ~50-70%.

Usa pdftotext (Poppler) como opción preferida por no tener conflictos de deps.
Fallback: pdfminer.six si está disponible sin conflictos.

Secciones extraídas: abstract, introducción, métodos, resultados, conclusiones
Secciones omitidas: referencias, apéndices, tablas de contenidos, portadas

Uso:
    python scripts/extract_pdf_essence.py <ruta-pdf>

Retorna texto limpio para pasar a Claude.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


KEYWORDS_START = {
    "abstract", "resumen", "summary", "executive summary",
    "introduction", "introducción", "related work",
    "method", "metodología", "methodology", "approach",
    "algorithm", "sistema", "system", "background"
}

KEYWORDS_END = {
    "references", "bibliography", "bibliografía", "cited works",
    "appendix", "apéndice", "supplementary", "suplementario",
    "acknowledgment", "agradecimientos", "author contributions",
    "data availability", "funding"
}


def filter_essential_content(text: str) -> str:
    """Extrae solo secciones esenciales, omitiendo referencias y apéndices."""
    lines = text.split('\n')
    result = []
    found_start = False

    for line in lines:
        lower = line.lower().strip()

        # Detectar fin del contenido principal
        if lower and any(kw in lower for kw in KEYWORDS_END):
            break

        # Detectar inicio del contenido principal
        if lower and any(kw in lower for kw in KEYWORDS_START):
            found_start = True

        # Incluir líneas después del inicio o que contengan keywords de inicio
        if found_start or (lower and any(kw in lower for kw in KEYWORDS_START)):
            if line.strip():
                result.append(line)

    return "\n".join(result)


def extract_pdf_text(pdf_path: Path) -> str:
    """Extrae texto esencial del PDF con estrategia fallback."""
    if not pdf_path.exists():
        raise FileNotFoundError(f"{pdf_path} no existe")

    # Estrategia 1: pdftotext (Poppler) - más ligero, sin deps Python complejas
    if shutil.which("pdftotext"):
        try:
            result = subprocess.run(
                ["pdftotext", str(pdf_path), "-"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0 and result.stdout:
                return filter_essential_content(result.stdout)
        except (subprocess.TimeoutExpired, Exception):
            pass

    # Estrategia 2: pdfminer.six (solo si existe y pdftotext no funcionó)
    try:
        from pdfminer.high_level import extract_text
        text = extract_text(str(pdf_path))
        if text:
            return filter_essential_content(text)
    except Exception:
        # Silenciar cualquier error de import o ejecución
        pass

    # Si ambas fallan
    raise RuntimeError(
        f"No se pudo extraer PDF. Opciones:\n"
        "  1. Instala pdftotext: apt-get install poppler-utils\n"
        "  2. O instala pdfminer.six: pip install pdfminer.six\n"
        "  3. O usa: Read el PDF en Claude Code directamente"
    )


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 1

    pdf_path = Path(sys.argv[1])
    try:
        content = extract_pdf_text(pdf_path)
        print(content)
        return 0
    except (FileNotFoundError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
