#!/usr/bin/env python3
"""Valida que un artículo en articles/<slug>/ cumple la constitución del repo.

Ejecuta las mismas comprobaciones que la CI y que el comando /vigilar-articulo,
para poder verificar un artículo en local antes de abrir un PR:

    python scripts/validate_article.py articles/<slug> [articles/<otro-slug> ...]
    python scripts/validate_article.py --changed

Ver CONSTITUTION.md para el detalle normativo de cada regla.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
TAXONOMY_PATH = REPO_ROOT / "taxonomy.yaml"
REQUIRED_FILES = ["metadata.yaml", "summary.md", "notebook.ipynb", "data/README.md"]
REQUIRED_METADATA_KEYS = [
    "title",
    "authors",
    "source_url",
    "date_added",
    "keywords",
    "status",
    "data_source",
    "entry_type",
    "year",
]
ALLOWED_ENTRY_TYPES = {"article", "inproceedings", "techreport", "misc"}


def load_taxonomy_keywords(taxonomy_path: Path) -> set[str]:
    data = yaml.safe_load(taxonomy_path.read_text()) or {}
    return {entry["name"] for entry in data.get("keywords", [])}


def find_changed_article_dirs(repo_root: Path) -> list[Path]:
    changed_files: set[str] = set()

    for cmd in (["git", "diff", "--name-only", "--cached"], ["git", "diff", "--name-only"]):
        result = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True)
        if result.returncode == 0:
            changed_files.update(line for line in result.stdout.splitlines() if line)

    merge_base = subprocess.run(
        ["git", "merge-base", "HEAD", "origin/main"], cwd=repo_root, capture_output=True, text=True
    )
    if merge_base.returncode == 0:
        base_sha = merge_base.stdout.strip()
        diff = subprocess.run(
            ["git", "diff", "--name-only", f"{base_sha}..HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        if diff.returncode == 0:
            changed_files.update(line for line in diff.stdout.splitlines() if line)

    dirs: set[Path] = set()
    for file_path in changed_files:
        parts = Path(file_path).parts
        if len(parts) >= 2 and parts[0] == "articles":
            dirs.add(repo_root / parts[0] / parts[1])
    return sorted(dirs)


def _run(
    cmd: list[str], cwd: Path, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)


def check_required_files(article_dir: Path) -> list[str]:
    errors = []
    for rel in REQUIRED_FILES:
        if not (article_dir / rel).is_file():
            errors.append(f"falta {rel}")
    return errors


def check_no_source_pdfs(article_dir: Path) -> list[str]:
    pdfs = sorted(article_dir.rglob("*.pdf")) + sorted(article_dir.rglob("*.PDF"))
    if pdfs:
        names = ", ".join(str(p.relative_to(article_dir)) for p in pdfs)
        return [f"no se debe commitear el PDF/texto original del artículo (encontrado: {names})"]
    return []


def check_src_or_not_feasible(article_dir: Path) -> tuple[list[str], bool]:
    has_src = (article_dir / "src").is_dir()
    has_not_feasible = (article_dir / "NOT_FEASIBLE.md").is_file()
    if has_src and has_not_feasible:
        return ["no puede existir src/ y NOT_FEASIBLE.md a la vez"], has_src
    if not has_src and not has_not_feasible:
        return ["debe existir src/ (código de reuso) o NOT_FEASIBLE.md (justificación)"], has_src
    return [], has_src


def check_metadata(article_dir: Path, taxonomy_keywords: set[str]) -> list[str]:
    metadata_path = article_dir / "metadata.yaml"
    if not metadata_path.is_file():
        return []

    errors = []
    try:
        metadata = yaml.safe_load(metadata_path.read_text()) or {}
    except yaml.YAMLError as exc:
        return [f"metadata.yaml inválido: {exc}"]

    if not isinstance(metadata, dict):
        return ["metadata.yaml debe contener un mapping YAML"]

    for key in REQUIRED_METADATA_KEYS:
        if key not in metadata:
            errors.append(f"falta la clave '{key}' en metadata.yaml")

    keywords = metadata.get("keywords")
    if not isinstance(keywords, list) or not keywords:
        errors.append("'keywords' debe ser una lista no vacía en metadata.yaml")
    else:
        unknown = [kw for kw in keywords if kw not in taxonomy_keywords]
        if unknown:
            errors.append(
                f"keywords no presentes en taxonomy.yaml: {', '.join(unknown)} "
                "(añádelas a taxonomy.yaml o usa una existente)"
            )

    entry_type = metadata.get("entry_type")
    if entry_type is not None and entry_type not in ALLOWED_ENTRY_TYPES:
        errors.append(
            f"'entry_type' debe ser uno de {sorted(ALLOWED_ENTRY_TYPES)}, no '{entry_type}'"
        )

    return errors


def check_ruff(src_dir: Path) -> list[str]:
    errors = []
    check = _run(["ruff", "check", str(src_dir)], cwd=REPO_ROOT)
    if check.returncode != 0:
        errors.append(f"ruff check falló en {src_dir}:\n{check.stdout}{check.stderr}")

    fmt = _run(["ruff", "format", "--check", str(src_dir)], cwd=REPO_ROOT)
    if fmt.returncode != 0:
        errors.append(f"ruff format --check falló en {src_dir}:\n{fmt.stdout}{fmt.stderr}")

    return errors


def check_tests_and_coverage(article_dir: Path) -> list[str]:
    errors = []
    tests_dir = article_dir / "tests"
    requirements = article_dir / "requirements.txt"

    if not tests_dir.is_dir():
        errors.append("falta tests/ (obligatorio si existe src/)")
    if not requirements.is_file():
        errors.append("falta requirements.txt (obligatorio si existe src/)")

    if not tests_dir.is_dir():
        return errors

    env = os.environ.copy()
    env["PYTHONPATH"] = str(article_dir) + os.pathsep + env.get("PYTHONPATH", "")
    result = _run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests",
            "--cov=src",
            "--cov-report=term-missing",
            "--cov-fail-under=100",
        ],
        cwd=article_dir,
        env=env,
    )
    (article_dir / ".coverage").unlink(missing_ok=True)
    if result.returncode != 0:
        errors.append(f"pytest/cobertura falló en {article_dir}:\n{result.stdout}{result.stderr}")

    return errors


def check_notebook_executes(notebook_path: Path) -> list[str]:
    if not notebook_path.is_file():
        return []

    try:
        import nbformat
        from nbclient import NotebookClient
        from nbclient.exceptions import CellExecutionError
    except ImportError:
        return [
            "no se puede ejecutar notebook.ipynb: faltan nbformat/nbclient/ipykernel "
            "en el entorno de validación"
        ]

    notebook = nbformat.read(notebook_path, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=120,
        kernel_name="python3",
        resources={"metadata": {"path": str(notebook_path.parent)}},
    )
    try:
        client.execute()
    except CellExecutionError as exc:
        return [f"notebook.ipynb no ejecuta de principio a fin sin errores:\n{exc}"]

    return []


def validate_article(article_dir: Path, taxonomy_keywords: set[str]) -> list[str]:
    if not article_dir.is_dir():
        return [f"{article_dir}: no es un directorio"]

    errors: list[str] = []
    errors += check_required_files(article_dir)
    errors += check_no_source_pdfs(article_dir)

    src_or_feasible_errors, has_src = check_src_or_not_feasible(article_dir)
    errors += src_or_feasible_errors

    errors += check_metadata(article_dir, taxonomy_keywords)

    if has_src:
        errors += check_ruff(article_dir / "src")
        errors += check_tests_and_coverage(article_dir)

    errors += check_notebook_executes(article_dir / "notebook.ipynb")

    return [f"{article_dir}: {error}" for error in errors]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "articles", nargs="*", type=Path, help="Rutas a directorios articles/<slug> a validar"
    )
    parser.add_argument(
        "--changed",
        action="store_true",
        help="Detectar automáticamente los artículos modificados vía git",
    )
    args = parser.parse_args()

    article_dirs = [p.resolve() for p in args.articles]
    if args.changed:
        article_dirs += find_changed_article_dirs(REPO_ROOT)

    article_dirs = sorted(set(article_dirs))
    if not article_dirs:
        print("No hay artículos que validar.")
        return 0

    taxonomy_keywords = load_taxonomy_keywords(TAXONOMY_PATH)

    all_errors: list[str] = []
    for article_dir in article_dirs:
        errors = validate_article(article_dir, taxonomy_keywords)
        if errors:
            all_errors.extend(errors)
        else:
            print(f"OK  {article_dir}")

    if all_errors:
        print("\nErrores encontrados:\n", file=sys.stderr)
        for error in all_errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
