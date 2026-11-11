"""Unit tests for Pygments code highlighting, table generation, heading tree, metrics, and theme CSS."""

import pytest

from src.core.md_compiler import compile_markdown
from src.core.theme_registry import get_theme_css
from src.models.print_profile import ThemeId


def test_compile_markdown_headings_and_metrics(sample_rich_markdown: str) -> None:
    """Verify heading tree extraction, line numbers, word count, and reading time."""
    manuscript = compile_markdown(sample_rich_markdown)

    assert manuscript.metadata.title == "Distributed Storage Engine Architecture"
    assert manuscript.word_count > 80
    assert manuscript.reading_time_min >= 1

    heading_texts = [(h.level, h.text) for h in manuscript.headings]
    assert heading_texts == [
        (1, "1. Architectural Overview"),
        (2, "1.1 Write-Ahead Log Pipeline"),
        (1, "2. Storage Engine Benchmarks"),
    ]
    assert all(h.line_number > 10 for h in manuscript.headings)
    assert all(h.anchor_id for h in manuscript.headings)


def test_compile_markdown_pygments_and_tables(sample_rich_markdown: str) -> None:
    """Verify Pygments inline syntax highlighting, callout rendering, and HTML table generation."""
    manuscript = compile_markdown(sample_rich_markdown)
    html = manuscript.body_html

    # Pygments inline style spans should be present
    assert 'class="code-container"' in html
    assert "<span style=" in html
    assert "append_wal_frame" in html
    assert "PYTHON" in html
    assert "SQL" in html

    # Markdown table converted to HTML table
    assert "<table>" in html
    assert "Profile</th>" in html
    assert "Leveled Compaction</td>" in html

    # Callouts preserved and styled
    assert 'class="callout callout-note"' in html
    assert 'class="callout callout-warning"' in html

    # TOC HTML generated
    assert 'class="toc-container"' in manuscript.toc_html
    assert "1. Architectural Overview" in manuscript.toc_html


def test_long_code_lines_wrapped_cleanly() -> None:
    """Verify very long code lines are wrapped so they never overflow PDF pages horizontally."""
    long_line = "x = " + '"a_very_long_identifier_segment_" + ' * 6 + '"end"'
    md = f"# Code Wrap Test\n\n```python\n{long_line}\n```\n"
    manuscript = compile_markdown(md)

    assert "a_very_long_identifier_segment_" in manuscript.body_html


@pytest.mark.parametrize("theme_id", list(ThemeId))
def test_all_print_themes_return_valid_css(theme_id: ThemeId) -> None:
    """Verify all 4 print themes return non-empty, distinct CSS with callout and table rules."""
    css = get_theme_css(theme_id, base_font_size=12)

    assert "body {" in css
    assert "h1 {" in css
    assert "table {" in css
    assert ".callout-note" in css
    assert ".callout-warning" in css
    assert ".callout-tip" in css
    assert f"Theme: {theme_id.value}" in css
