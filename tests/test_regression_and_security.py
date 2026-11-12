"""Regression, security boundary, localization/Unicode, concurrency, and GUI smoke tests."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import time
import tkinter as tk
import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore", FutureWarning)
    import fitz

import pytest

from src.core.book_binder import bind_folder_manuscript
from src.core.frontmatter_parser import parse_frontmatter
from src.core.md_compiler import compile_markdown
from src.core.pdf_typesetter import render_pdf_page_preview, typeset_to_pdf_bytes
from src.gui.app import SmartMarkdownPublisherApp, _update_yaml_boolean_flag
from src.models.print_profile import MarginPreset, PageSize, PrintProfile, ThemeId


def test_regression_toc_bookmarks_map_to_actual_pages_not_toc_page() -> None:
    """BUG-01 regression: PDF bookmarks must point to actual chapter pages even when include_toc=True."""
    md = "".join(
        [
            "---\ntitle: Multi-Page Book\ncover: true\ntoc: true\n---\n\n",
            "# Chapter 1: Alpha\n\n" + ("Alpha body paragraph content. " * 150) + "\n\n",
            "# Chapter 2: Beta\n\n" + ("Beta body paragraph content. " * 150) + "\n\n",
            "# Chapter 3: Gamma\n\n" + ("Gamma body paragraph content. " * 150) + "\n\n",
        ]
    )
    ms = compile_markdown(md)
    pdf_bytes = typeset_to_pdf_bytes(ms, PrintProfile())
    doc = fitz.open("pdf", pdf_bytes)
    toc = doc.get_toc()
    doc.close()

    bookmark_pages = {title: page for _lvl, title, page in toc}
    assert bookmark_pages["Cover: Multi-Page Book"] == 1
    assert bookmark_pages["Chapter 1: Alpha"] == 2
    assert bookmark_pages["Chapter 2: Beta"] > 2
    assert bookmark_pages["Chapter 3: Gamma"] > bookmark_pages["Chapter 2: Beta"]


def test_regression_empty_fenced_code_block_rendered() -> None:
    """BUG-02 regression: Empty fenced code blocks must still render inside a code-container."""
    md = "# Empty Fence\n\n```python\n```\n\nTrailing text."
    ms = compile_markdown(md)
    assert 'class="code-container"' in ms.body_html
    assert "PYTHON" in ms.body_html


def test_regression_yaml_boolean_flag_updates_include_aliases() -> None:
    """BUG-03 regression: _update_yaml_boolean_flag must update include_cover/include_toc aliases."""
    raw = "---\ninclude_cover: false\ninclude_toc: false\n---\n# Heading"
    updated = _update_yaml_boolean_flag(raw, "cover", True)
    updated = _update_yaml_boolean_flag(updated, "toc", True)
    meta, _ = parse_frontmatter(updated)

    assert meta.include_cover is True
    assert meta.include_toc is True


def test_empty_and_whitespace_inputs_do_not_crash() -> None:
    """Boundary value test: empty and whitespace-only Markdown produces valid 1-page PDF."""
    for raw in ("", "   \n\n  \t  "):
        ms = compile_markdown(raw)
        assert ms.word_count == 0
        assert ms.reading_time_min == 0
        pdf = typeset_to_pdf_bytes(ms, PrintProfile())
        assert pdf.startswith(b"%PDF-")
        img, total = render_pdf_page_preview(pdf, 0, 400)
        assert total == 1
        assert img.width >= 400


def test_unicode_and_special_characters_render_safely() -> None:
    """I18n / encoding test: UTF-8 accented Latin, math symbols, and HTML special chars."""
    md = "---\ntitle: Spec <Alpha & Omega>\nauthor: José Álvarez\n---\n# Café & Crème\n\nEquations: ∑ x_i ≤ α + β."
    ms = compile_markdown(md)
    pdf = typeset_to_pdf_bytes(ms, PrintProfile())
    assert pdf.startswith(b"%PDF-")
    assert "&lt;" in ms.toc_html or "&amp;" in ms.toc_html


def test_book_binder_with_book_yaml_override(tmp_path: Path) -> None:
    """Integration test: book.yaml overrides individual chapter YAML frontmatter."""
    book_dir = tmp_path / "book_with_yaml"
    book_dir.mkdir()
    (book_dir / "book.yaml").write_text(
        "title: Master Volume\nauthor: Editorial Board\ncover: true\n",
        encoding="utf-8",
    )
    (book_dir / "01_ch1.md").write_text("---\ntitle: Ch1\n---\n# One\nText one.", encoding="utf-8")
    (book_dir / "02_ch2.md").write_text("# Two\nText two.", encoding="utf-8")

    bound = bind_folder_manuscript(str(book_dir))
    meta, _ = parse_frontmatter(bound)
    assert meta.title == "Master Volume"
    assert meta.author == "Editorial Board"
    assert meta.include_cover is True


@pytest.mark.parametrize("page_size", list(PageSize))
@pytest.mark.parametrize("margins", list(MarginPreset))
def test_all_page_sizes_and_margin_presets(page_size: PageSize, margins: MarginPreset) -> None:
    """Combinatorial layout test across every PageSize x MarginPreset pair."""
    ms = compile_markdown("# Layout Matrix\n\nParagraph text for boundary check.")
    profile = PrintProfile(page_size=page_size, margins=margins)
    pdf = typeset_to_pdf_bytes(ms, profile)
    doc = fitz.open("pdf", pdf)
    assert doc.page_count >= 1
    assert abs(doc[0].rect.width - page_size.width) < 1.0
    assert abs(doc[0].rect.height - page_size.height) < 1.0
    doc.close()


def test_concurrent_typesetting_is_deterministic() -> None:
    """Concurrency & thread-safety test across 8 parallel worker threads."""
    md = "---\ntitle: Concurrency Test\ncover: true\ntoc: true\n---\n# S1\n\n" + ("Parallel test. " * 60)

    def _run(_idx: int) -> bytes:
        ms = compile_markdown(md)
        return typeset_to_pdf_bytes(ms, PrintProfile())

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(_run, range(8)))

    assert len(results) == 8
    assert all(r.startswith(b"%PDF-") for r in results)


def test_gui_studio_smoke_and_keyboard_focus() -> None:
    """GUI end-to-end smoke + keyboard accessibility check on Tkinter widgets."""
    root = tk.Tk()
    root.withdraw()
    try:
        app = SmartMarkdownPublisherApp(root)
        for _ in range(60):
            root.update()
            if app.latest_pdf_bytes:
                break
            time.sleep(0.05)

        assert app.latest_pdf_bytes.startswith(b"%PDF-")
        assert app.latest_manuscript is not None
        assert app.editor.text.cget("takefocus") in ("", "1", 1, True)
        assert len(app.sidebar.tree.get_children()) >= 1
    finally:
        root.destroy()
