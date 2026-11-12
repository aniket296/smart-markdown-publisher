"""PyMuPDF (fitz.Story) PDF Typesetter with vector Cover Page, TOC, running headers/footers, and outline bookmarks."""

from datetime import date
import io
from pathlib import Path
from typing import Optional
import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore", FutureWarning)
    import fitz

from PIL import Image, ImageOps

from src.core.theme_registry import get_theme_css
from src.models.document_model import CompiledManuscript, HeadingNode
from src.models.print_profile import PrintProfile, ThemeId


def _get_theme_accent_rgb(theme: ThemeId) -> tuple[float, float, float]:
    """Return normalized RGB (0..1) primary accent color for the selected theme."""
    if theme == ThemeId.ACADEMIC:
        return (0.12, 0.16, 0.23)  # Classic Charcoal / Slate (#1E293B)
    if theme == ThemeId.EXECUTIVE:
        return (0.12, 0.23, 0.54)  # Executive Navy (#1E3A8A)
    if theme == ThemeId.COMPACT:
        return (0.06, 0.46, 0.43)  # Deep Teal (#0F766E)
    return (0.05, 0.58, 0.53)      # Technical Teal (#0D9488)


def _draw_cover_page(
    doc: fitz.Document,
    manuscript: CompiledManuscript,
    profile: PrintProfile,
) -> None:
    """Render a dedicated, professionally typeset vector Cover Page on Page 1."""
    page_w = float(profile.page_size.width)
    page_h = float(profile.page_size.height)
    margin = float(profile.margins.points)

    page = doc.new_page(width=page_w, height=page_h)
    meta = manuscript.metadata
    accent_rgb = _get_theme_accent_rgb(profile.theme)
    dark_slate = (0.06, 0.09, 0.16)  # #0F172A
    muted_slate = (0.28, 0.33, 0.41)  # #475569
    light_bg = (0.97, 0.98, 0.99)     # #F8FAFC

    # Subtle page background tint and left vertical spine bar
    shape = page.new_shape()
    shape.draw_rect(fitz.Rect(0, 0, page_w, page_h))
    shape.finish(fill=light_bg, color=None)

    # Left vertical accent bar
    shape.draw_rect(fitz.Rect(0, 0, 18, page_h))
    shape.finish(fill=dark_slate, color=None)
    shape.draw_rect(fitz.Rect(18, 0, 24, page_h))
    shape.finish(fill=accent_rgb, color=None)

    # Top decorative rule and institution / version badge
    content_left = max(margin + 18, 68.0)
    content_right = page_w - margin

    shape.draw_line(fitz.Point(content_left, margin + 20), fitz.Point(content_right, margin + 20))
    shape.finish(color=accent_rgb, width=2.0)
    shape.commit()

    font_bold = "tiro" if profile.theme == ThemeId.ACADEMIC else "hebo"
    font_reg = "tiro" if profile.theme == ThemeId.ACADEMIC else "helv"

    if meta.institution:
        page.insert_text(
            fitz.Point(content_left, margin + 12),
            meta.institution.upper(),
            fontsize=9.5,
            fontname=font_bold,
            color=accent_rgb,
        )

    # Main Title block (supports multi-line wrapping via insert_textbox)
    title_top = page_h * 0.26
    title_rect = fitz.Rect(content_left, title_top, content_right, title_top + 140)
    page.insert_textbox(
        title_rect,
        meta.title or "Untitled Document",
        fontsize=26,
        fontname=font_bold,
        color=dark_slate,
        align=fitz.TEXT_ALIGN_LEFT,
    )

    # Subtitle block
    if meta.subtitle:
        sub_rect = fitz.Rect(content_left, title_top + 110, content_right, title_top + 185)
        page.insert_textbox(
            sub_rect,
            meta.subtitle,
            fontsize=14,
            fontname=font_reg,
            color=muted_slate,
            align=fitz.TEXT_ALIGN_LEFT,
        )

    # Middle accent divider bar
    divider_y = title_top + 195
    div_shape = page.new_shape()
    div_shape.draw_rect(fitz.Rect(content_left, divider_y, content_left + 85, divider_y + 4))
    div_shape.finish(fill=accent_rgb, color=None)
    div_shape.commit()

    # Bottom Metadata Block (Author, Date, Version)
    meta_top = page_h - margin - 135
    meta_box = fitz.Rect(content_left, meta_top, content_right, page_h - margin - 20)
    box_shape = page.new_shape()
    box_shape.draw_rect(meta_box)
    box_shape.finish(fill=(0.94, 0.96, 0.98), color=(0.80, 0.84, 0.88), width=0.75)
    box_shape.commit()

    y_cursor = meta_top + 24
    if meta.author:
        page.insert_text(
            fitz.Point(content_left + 16, y_cursor),
            f"AUTHOR:  {meta.author}",
            fontsize=10.5,
            fontname=font_bold,
            color=dark_slate,
        )
        y_cursor += 22

    display_date = meta.date or date.today().isoformat()
    page.insert_text(
        fitz.Point(content_left + 16, y_cursor),
        f"DATE:      {display_date}",
        fontsize=10,
        fontname=font_reg,
        color=muted_slate,
    )
    y_cursor += 20

    if meta.version:
        page.insert_text(
            fitz.Point(content_left + 16, y_cursor),
            f"VERSION: {meta.version}",
            fontsize=10,
            fontname=font_reg,
            color=muted_slate,
        )
        y_cursor += 20

    page.insert_text(
        fitz.Point(content_left + 16, y_cursor),
        f"PROFILE: {profile.theme.value}  |  {profile.page_size.name}",
        fontsize=8.5,
        fontname=font_reg,
        color=accent_rgb,
    )


def _stamp_headers_and_footers(
    doc: fitz.Document,
    manuscript: CompiledManuscript,
    profile: PrintProfile,
    start_page_idx: int,
) -> None:
    """Two-pass stamping of running headers and `Page X of Y` footers on content pages."""
    total_content_pages = len(doc) - start_page_idx
    if total_content_pages <= 0:
        return

    page_w = float(profile.page_size.width)
    page_h = float(profile.page_size.height)
    margin = float(profile.margins.points)
    meta = manuscript.metadata

    header_color = (0.39, 0.45, 0.55)  # #64748B
    rule_color = (0.80, 0.84, 0.88)    # #CBD5E1

    left_header = (meta.title or "Untitled Document")[:65]
    right_header = (meta.header_text or meta.date or meta.version or "")[:45]
    left_footer = (meta.footer_text or meta.institution or meta.author or "")[:60]

    for idx in range(start_page_idx, len(doc)):
        page = doc[idx]
        content_page_num = idx - start_page_idx + 1

        if profile.show_running_header:
            header_y = max(20.0, margin - 16.0)
            rule_y = header_y + 5.0

            page.insert_text(
                fitz.Point(margin, header_y),
                left_header,
                fontsize=8.0,
                fontname="helv",
                color=header_color,
            )
            if right_header:
                right_rect = fitz.Rect(page_w * 0.5, header_y - 10.0, page_w - margin, header_y + 4.0)
                page.insert_textbox(
                    right_rect,
                    right_header,
                    fontsize=8.0,
                    fontname="helv",
                    color=header_color,
                    align=fitz.TEXT_ALIGN_RIGHT,
                )

            shape = page.new_shape()
            shape.draw_line(fitz.Point(margin, rule_y), fitz.Point(page_w - margin, rule_y))
            shape.finish(color=rule_color, width=0.5)
            shape.commit()

        if profile.show_page_numbers or left_footer:
            footer_rule_y = page_h - max(24.0, margin - 10.0)
            footer_text_y = footer_rule_y + 12.0

            shape = page.new_shape()
            shape.draw_line(
                fitz.Point(margin, footer_rule_y),
                fitz.Point(page_w - margin, footer_rule_y),
            )
            shape.finish(color=rule_color, width=0.5)
            shape.commit()

            if left_footer:
                page.insert_text(
                    fitz.Point(margin, footer_text_y),
                    left_footer,
                    fontsize=8.0,
                    fontname="helv",
                    color=header_color,
                )

            if profile.show_page_numbers:
                page_label = f"Page {content_page_num} of {total_content_pages}"
                label_width = fitz.get_text_length(page_label, fontname="helv", fontsize=8.5)
                x_pos = page_w - margin - label_width
                page.insert_text(
                    fitz.Point(x_pos, footer_text_y),
                    page_label,
                    fontsize=8.5,
                    fontname="helv",
                    color=(0.18, 0.25, 0.33),
                )


def _strip_toc_lines_from_page_texts(
    page_texts: list[str],
    headings: list[HeadingNode],
    start_page_idx: int,
) -> list[str]:
    """Remove rendered Table of Contents lines from page_texts so bookmarks match actual heading pages."""
    cleaned = list(page_texts)
    toc_titles = [h.text.strip() for h in headings if h.level <= 4 and h.text.strip()]
    if not toc_titles:
        return cleaned

    in_toc = False
    toc_cursor = 0
    for p_idx in range(start_page_idx, len(cleaned)):
        lines = cleaned[p_idx].splitlines()
        kept_lines: list[str] = []
        for line in lines:
            stripped = line.strip()
            if not in_toc and stripped.lower() == "table of contents":
                in_toc = True
                continue
            if in_toc and toc_cursor < len(toc_titles):
                if stripped.lower() == toc_titles[toc_cursor].lower():
                    toc_cursor += 1
                    continue
            kept_lines.append(line)
        cleaned[p_idx] = "\n".join(kept_lines)
        if toc_cursor >= len(toc_titles):
            break
    return cleaned


def _map_headings_to_pdf_toc(
    doc: fitz.Document,
    headings: list[HeadingNode],
    start_page_idx: int,
    strip_toc: bool = False,
) -> list[list[int | str]]:
    """Map manuscript HeadingNodes to their 1-based PDF page numbers and normalize hierarchy for doc.set_toc()."""
    if not headings or len(doc) == 0:
        return []

    # Pre-extract text per page for fast lookup
    page_texts: list[str] = [doc[i].get_text("text") for i in range(len(doc))]
    if strip_toc:
        page_texts = _strip_toc_lines_from_page_texts(page_texts, headings, start_page_idx)
    search_cursor = start_page_idx

    raw_entries: list[tuple[int, str, int]] = []
    for h in headings:
        found_page_1based = start_page_idx + 1
        target = h.text.strip()
        if target:
            for p_idx in range(search_cursor, len(doc)):
                if target.lower() in page_texts[p_idx].lower():
                    found_page_1based = p_idx + 1
                    search_cursor = p_idx
                    break
            else:
                # Fallback search across all content pages
                for p_idx in range(start_page_idx, len(doc)):
                    if target.lower() in page_texts[p_idx].lower():
                        found_page_1based = p_idx + 1
                        break

        raw_entries.append((h.level, target or "Section", found_page_1based))

    # PyMuPDF doc.set_toc() requires the first item to have level 1 and subsequent levels
    # to increase by at most 1 step at a time.
    normalized_toc: list[list[int | str]] = []
    prev_level = 0
    for level, title, page_num in raw_entries:
        if not normalized_toc:
            norm_level = 1
        elif level > prev_level + 1:
            norm_level = prev_level + 1
        else:
            norm_level = max(1, level)
        normalized_toc.append([norm_level, title, page_num])
        prev_level = norm_level

    return normalized_toc


def typeset_to_pdf_bytes(
    manuscript: CompiledManuscript,
    profile: PrintProfile | None = None,
    asset_dir: Optional[str] = None,
) -> bytes:
    """Typeset a CompiledManuscript into publication-ready PDF bytes using PyMuPDF fitz.Story."""
    active_profile = profile or PrintProfile()
    page_w = float(active_profile.page_size.width)
    page_h = float(active_profile.page_size.height)
    margin = float(active_profile.margins.points)

    doc = fitz.open()

    # 1. Optional Cover Page
    if manuscript.metadata.include_cover:
        _draw_cover_page(doc, manuscript, active_profile)

    content_start_page_idx = len(doc)

    # 2. Assemble HTML Document (with optional Table of Contents prepended)
    toc_section = (
        manuscript.toc_html
        if (manuscript.metadata.include_toc and manuscript.toc_html)
        else ""
    )
    full_body_html = (
        "<!DOCTYPE html><html><head><meta charset='utf-8'></head><body>"
        f"{toc_section}"
        f"{manuscript.body_html or '<p></p>'}"
        "</body></html>"
    )

    theme_css = get_theme_css(
        active_profile.theme,
        base_font_size=active_profile.base_font_size,
    )

    archive = None
    if asset_dir:
        asset_path = Path(asset_dir)
        if asset_path.exists() and asset_path.is_dir():
            archive = fitz.Archive(str(asset_path.resolve()))

    # 3. Story Pagination Loop
    story = fitz.Story(html=full_body_html, user_css=theme_css, archive=archive)
    mediabox = fitz.Rect(0, 0, page_w, page_h)
    # Reserve vertical breathing room for running header and footer
    top_inset = margin + (10.0 if active_profile.show_running_header else 0.0)
    bottom_inset = margin + (12.0 if active_profile.show_page_numbers else 0.0)
    where_rect = fitz.Rect(margin, top_inset, page_w - margin, page_h - bottom_inset)

    writerBuffer = io.BytesIO()
    writer = fitz.DocumentWriter(writerBuffer)

    more = 1
    safety_page_cap = 500
    pages_generated = 0
    while more and pages_generated < safety_page_cap:
        dev = writer.begin_page(mediabox)
        more, _ = story.place(where_rect)
        story.draw(dev)
        writer.end_page()
        pages_generated += 1

    writer.close()

    # Merge Story-paginated pages into main document
    writerBuffer.seek(0)
    story_doc = fitz.open("pdf", writerBuffer.read())
    if len(story_doc) > 0:
        doc.insert_pdf(story_doc)
    story_doc.close()

    # Ensure at least one content page exists
    if len(doc) == content_start_page_idx:
        doc.new_page(width=page_w, height=page_h)

    # 4. Two-Pass Running Headers & `Page X of Y` Footers
    _stamp_headers_and_footers(doc, manuscript, active_profile, content_start_page_idx)

    # 5. Clickable PDF Bookmarks (doc.set_toc())
    toc_entries = _map_headings_to_pdf_toc(
        doc,
        manuscript.headings,
        content_start_page_idx,
        strip_toc=bool(toc_section),
    )
    if toc_entries:
        if manuscript.metadata.include_cover:
            toc_entries.insert(0, [1, f"Cover: {manuscript.metadata.title}", 1])
        doc.set_toc(toc_entries)

    pdf_bytes = doc.tobytes(garbage=4, deflate=True)
    doc.close()
    return pdf_bytes


def render_pdf_page_preview(
    pdf_bytes: bytes,
    page_index: int = 0,
    max_width: int = 520,
) -> tuple[Image.Image, int]:
    """Render a specific page from pdf_bytes to a PIL Image scaled to max_width with a subtle border."""
    if not pdf_bytes:
        raise ValueError("Cannot render preview from empty pdf_bytes")

    doc = fitz.open("pdf", pdf_bytes)
    total_pages = len(doc)
    if total_pages == 0:
        doc.close()
        raise ValueError("PDF document has zero pages")

    clamped_idx = max(0, min(page_index, total_pages - 1))
    page = doc[clamped_idx]
    rect = page.rect
    scale = max(0.5, float(max_width) / max(1.0, rect.width))
    matrix = fitz.Matrix(scale, scale)
    pix = page.get_pixmap(matrix=matrix, alpha=False)

    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    doc.close()

    # Add a crisp 1px slate page border
    bordered = ImageOps.expand(img, border=1, fill=(148, 163, 184))
    return bordered, total_pages
