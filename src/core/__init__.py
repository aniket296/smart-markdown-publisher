"""Core Markdown parsing, callout processing, theme compilation, and PDF typesetting."""

from src.core.book_binder import bind_folder_manuscript
from src.core.callout_processor import preprocess_callouts
from src.core.frontmatter_parser import parse_frontmatter
from src.core.md_compiler import compile_markdown
from src.core.pdf_typesetter import render_pdf_page_preview, typeset_to_pdf_bytes
from src.core.theme_registry import get_theme_css

__all__ = [
    "parse_frontmatter",
    "preprocess_callouts",
    "get_theme_css",
    "compile_markdown",
    "bind_folder_manuscript",
    "typeset_to_pdf_bytes",
    "render_pdf_page_preview",
]

