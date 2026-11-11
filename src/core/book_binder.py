"""Multi-chapter folder book binder for compiling ordered Markdown files into a single manuscript."""

from pathlib import Path
import re
from src.core.frontmatter_parser import parse_frontmatter

_NATURAL_SORT_RE = re.compile(r"(\d+)")

PAGE_BREAK_MARKER = '<div style="page-break-before: always;"></div>'


def _natural_sort_key(path: Path) -> list[int | str]:
    """Generate a natural sort key so 01_intro.md, 2_setup.md, 10_appendix.md sort in numeric order."""
    parts = _NATURAL_SORT_RE.split(path.name.lower())
    return [int(part) if part.isdigit() else part for part in parts]


def bind_folder_manuscript(folder_path: str) -> str:
    """Scan folder_path for .md files sorted naturally and concatenate them into a single manuscript.

    Preserves the first file's YAML frontmatter (or book.yaml if present) and separates
    subsequent chapter bodies with explicit page-break markers (`<div style="page-break-before: always;"></div>`).
    """
    folder = Path(folder_path).resolve()
    if not folder.exists() or not folder.is_dir():
        raise FileNotFoundError(f"Book folder not found: {folder_path}")

    md_files = sorted(
        [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in {".md", ".markdown"}],
        key=_natural_sort_key,
    )
    if not md_files:
        raise ValueError(f"No Markdown (.md) files found in folder: {folder_path}")

    # Check if an explicit book.yaml / book.yml exists
    book_yaml_path = None
    for candidate in ("book.yaml", "book.yml"):
        cand_path = folder / candidate
        if cand_path.is_file():
            book_yaml_path = cand_path
            break

    frontmatter_block = ""
    if book_yaml_path is not None:
        raw_book_yaml = book_yaml_path.read_text(encoding="utf-8").strip()
        if raw_book_yaml.startswith("---"):
            frontmatter_block = raw_book_yaml
        else:
            frontmatter_block = f"---\n{raw_book_yaml}\n---"

    chapters: list[str] = []
    for idx, md_file in enumerate(md_files):
        raw_chapter = md_file.read_text(encoding="utf-8")
        if idx == 0 and not frontmatter_block:
            # Keep the first file's YAML frontmatter if it has one
            if raw_chapter.lstrip("\ufeff").startswith("---"):
                _, body = parse_frontmatter(raw_chapter)
                yaml_end = len(raw_chapter) - len(body)
                frontmatter_block = raw_chapter[:yaml_end].strip()
                chapter_body = body.strip()
            else:
                chapter_body = raw_chapter.strip()
        else:
            _, chapter_body_raw = parse_frontmatter(raw_chapter)
            chapter_body = chapter_body_raw.strip()

        if chapter_body:
            chapters.append(chapter_body)

    joined_body = f"\n\n{PAGE_BREAK_MARKER}\n\n".join(chapters)
    if frontmatter_block:
        return f"{frontmatter_block}\n\n{joined_body}\n"
    return f"{joined_body}\n"
