"""Unit tests for YAML frontmatter parsing, callout processing, path resolution, and folder book binding."""

from pathlib import Path
import pytest

from src.core.book_binder import PAGE_BREAK_MARKER, bind_folder_manuscript
from src.core.callout_processor import preprocess_callouts
from src.core.frontmatter_parser import parse_frontmatter
from src.utils.path_resolver import resolve_markdown_image_paths


def test_parse_complete_frontmatter(sample_rich_markdown: str) -> None:
    """Verify full YAML frontmatter extraction and body separation."""
    meta, body = parse_frontmatter(sample_rich_markdown)

    assert meta.title == "Distributed Storage Engine Architecture"
    assert meta.subtitle == "Consensus, Write-Ahead Logging & B-Tree Compaction"
    assert meta.author == "Dr. Evelyn Vance"
    assert meta.date == "2026-11-12"
    assert meta.version == "2.4.0"
    assert meta.institution == "Systems Research Lab"
    assert meta.include_cover is True
    assert meta.include_toc is True
    assert meta.header_text == "CONFIDENTIAL TECHNICAL SPEC"
    assert meta.footer_text == "Systems Research Lab - Internal Distribution"
    assert not body.lstrip().startswith("---")
    assert "# 1. Architectural Overview" in body


def test_parse_frontmatter_fallback_to_h1() -> None:
    """Verify fallback to the first # H1 heading when YAML frontmatter is absent."""
    raw = "\n# High-Frequency Trading Kernel\n\nLow-latency ring buffer overview."
    meta, body = parse_frontmatter(raw)

    assert meta.title == "High-Frequency Trading Kernel"
    assert meta.include_cover is False
    assert meta.include_toc is False
    assert "# High-Frequency Trading Kernel" in body


def test_parse_malformed_frontmatter_does_not_crash() -> None:
    """Verify malformed YAML gracefully falls back without raising an exception."""
    malformed = "---\ntitle: [unclosed list\ninvalid_yaml: : : :\n---\n# Recovery Heading\nBody text."
    meta, body = parse_frontmatter(malformed)

    assert meta.title == "Recovery Heading"
    assert "Body text." in body


def test_preprocess_callouts_all_types_and_multiline() -> None:
    """Verify transformation of GitHub/Obsidian callouts into semantic print HTML containers."""
    md = """
> [!NOTE]
> Standard informational note.

> [!WARNING] Critical Thermal Threshold
> First warning paragraph.
>
> Second warning paragraph with `inline_code`.

> [!TIP]
> Helpful productivity tip.

> [!IMPORTANT]
> Mandatory compliance requirement.

> [!CAUTION]
> High voltage hazard.
"""
    html_out = preprocess_callouts(md)

    assert '<div class="callout callout-note">' in html_out
    assert '<p class="callout-title">NOTE</p>' in html_out
    assert '<div class="callout callout-warning">' in html_out
    assert '<p class="callout-title">Critical Thermal Threshold</p>' in html_out
    assert "<code>inline_code</code>" in html_out
    assert '<div class="callout callout-tip">' in html_out
    assert '<div class="callout callout-important">' in html_out
    assert '<div class="callout callout-caution">' in html_out


def test_resolve_relative_image_paths(tmp_path: Path) -> None:
    """Verify relative Markdown and HTML image paths resolve while URLs remain untouched."""
    md = (
        "![Architecture](./diagrams/arch.png)\n"
        "![Remote](https://example.org/logo.png)\n"
        '<img src="assets/figure1.jpg" alt="fig1">'
    )
    resolved = resolve_markdown_image_paths(md, str(tmp_path))
    expected_arch = (tmp_path / "diagrams" / "arch.png").resolve().as_posix()
    expected_fig = (tmp_path / "assets" / "figure1.jpg").resolve().as_posix()

    assert expected_arch in resolved
    assert expected_fig in resolved
    assert "https://example.org/logo.png" in resolved


def test_bind_folder_manuscript_natural_order(sample_chapter_folder: Path) -> None:
    """Verify multi-chapter folder binder sorts files naturally and preserves first frontmatter."""
    bound_md = bind_folder_manuscript(str(sample_chapter_folder))
    meta, body = parse_frontmatter(bound_md)

    assert meta.title == "Enterprise Systems Handbook"
    assert meta.author == "Principal Engineering Group"
    assert meta.include_cover is True

    # Ensure natural sort order: Chapter 1 -> Chapter 2 -> Chapter 10
    pos_ch1 = body.find("# Chapter 1: Introduction")
    pos_ch2 = body.find("# Chapter 2: Service Mesh Architecture")
    pos_ch10 = body.find("# Chapter 10: Operational Checklist")

    assert 0 <= pos_ch1 < pos_ch2 < pos_ch10
    assert body.count(PAGE_BREAK_MARKER) == 2
    assert "Ignored Chapter Override" not in body


def test_bind_folder_missing_raises(tmp_path: Path) -> None:
    """Verify bind_folder_manuscript raises ValueError on an empty folder."""
    empty_dir = tmp_path / "empty_book"
    empty_dir.mkdir()
    with pytest.raises(ValueError, match="No Markdown"):
        bind_folder_manuscript(str(empty_dir))
