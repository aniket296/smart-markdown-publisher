"""Unit tests for PyMuPDF Story PDF generation, cover page toggle, running footers, and PDF bookmarks."""

import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore", FutureWarning)
    import fitz

from src.core.md_compiler import compile_markdown
from src.core.pdf_typesetter import render_pdf_page_preview, typeset_to_pdf_bytes
from src.models.print_profile import MarginPreset, PageSize, PrintProfile, ThemeId


def test_typeset_to_pdf_bytes_end_to_end(sample_rich_markdown: str) -> None:
    """Verify end-to-end PDF byte stream generation, running footers, and native TOC bookmarks."""
    manuscript = compile_markdown(sample_rich_markdown)
    profile = PrintProfile(
        page_size=PageSize.A4,
        theme=ThemeId.TECHNICAL,
        margins=MarginPreset.STANDARD,
        show_page_numbers=True,
        show_running_header=True,
        base_font_size=11,
    )

    pdf_bytes = typeset_to_pdf_bytes(manuscript, profile)
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 2000

    doc = fitz.open("pdf", pdf_bytes)
    assert doc.page_count >= 2

    # Page 1 is the Cover Page (title may wrap across lines in insert_textbox)
    cover_text = " ".join(doc[0].get_text("text").split())
    assert "Distributed Storage Engine Architecture" in cover_text
    assert "Dr. Evelyn Vance" in cover_text

    # Page 2 is the first content page and must have `Page 1 of N` footer and running header
    content_p1_text = doc[1].get_text("text")
    total_content_pages = doc.page_count - 1
    assert f"Page 1 of {total_content_pages}" in content_p1_text
    assert "CONFIDENTIAL TECHNICAL SPEC" in content_p1_text

    # Verify clickable PDF bookmarks (outline tree)
    toc = doc.get_toc()
    assert len(toc) >= 4
    toc_titles = [entry[1] for entry in toc]
    assert any("1. Architectural Overview" in t for t in toc_titles)
    assert any("1.1 Write-Ahead Log Pipeline" in t for t in toc_titles)
    assert any("2. Storage Engine Benchmarks" in t for t in toc_titles)
    doc.close()


def test_cover_page_toggle_increases_page_count() -> None:
    """Verify enabling include_cover adds exactly one dedicated cover page."""
    md_without_cover = "---\ntitle: Short Technical Note\ncover: false\n---\n# Section One\n\nConcise body paragraph."
    md_with_cover = "---\ntitle: Short Technical Note\ncover: true\n---\n# Section One\n\nConcise body paragraph."

    ms_no_cover = compile_markdown(md_without_cover)
    ms_with_cover = compile_markdown(md_with_cover)

    pdf_no_cover = typeset_to_pdf_bytes(ms_no_cover, PrintProfile())
    pdf_with_cover = typeset_to_pdf_bytes(ms_with_cover, PrintProfile())

    doc_no = fitz.open("pdf", pdf_no_cover)
    doc_yes = fitz.open("pdf", pdf_with_cover)

    assert doc_yes.page_count == doc_no.page_count + 1
    doc_no.close()
    doc_yes.close()


def test_render_pdf_page_preview_returns_pil_image(sample_rich_markdown: str) -> None:
    """Verify render_pdf_page_preview produces a crisp bordered PIL image and total page count."""
    manuscript = compile_markdown(sample_rich_markdown)
    pdf_bytes = typeset_to_pdf_bytes(manuscript, PrintProfile(page_size=PageSize.LETTER))

    image, total_pages = render_pdf_page_preview(pdf_bytes, page_index=0, max_width=480)
    assert total_pages >= 2
    assert image.width >= 480
    assert image.height > image.width
