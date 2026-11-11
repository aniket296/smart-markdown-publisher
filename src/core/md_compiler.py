"""Markdown compiler with YAML frontmatter extraction, heading tree, callouts, and Pygments syntax highlighting."""

import html
import math
import re
import textwrap
from typing import Optional
import markdown
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer, get_lexer_by_name, guess_lexer
from pygments.util import ClassNotFound

from src.core.callout_processor import preprocess_callouts
from src.core.frontmatter_parser import parse_frontmatter
from src.models.document_model import CompiledManuscript, HeadingNode
from src.utils.path_resolver import resolve_markdown_image_paths

_HEADING_RE = re.compile(r"^[ \t]*(?P<hashes>#{1,6})[ \t]+(?P<text>[^\r\n#]+?)[ \t#]*$")
_FENCED_CODE_RE = re.compile(
    r"^(?P<fence>`{3,}|~{3,})[ \t]*(?P<lang>[a-zA-Z0-9_+-]*)[ \t]*\r?\n(?P<code>.*?)\r?\n(?P=fence)[ \t]*$",
    re.MULTILINE | re.DOTALL,
)
_WORD_RE = re.compile(r"\b[\w'-]+\b", re.UNICODE)


def _slugify(text: str, seen: dict[str, int]) -> str:
    """Create a deterministic, unique HTML anchor slug for a heading."""
    base = re.sub(r"[^a-zA-Z0-9\s-]", "", text.lower()).strip()
    base = re.sub(r"[\s_-]+", "-", base) or "section"
    count = seen.get(base, 0)
    seen[base] = count + 1
    return base if count == 0 else f"{base}-{count}"


def _extract_headings(raw_markdown: str) -> list[HeadingNode]:
    """Scan raw_markdown line-by-line (preserving exact editor line numbers) and extract H1-H6 HeadingNodes."""
    headings: list[HeadingNode] = []
    seen_slugs: dict[str, int] = {}
    in_frontmatter = False
    in_fence = False
    lines = raw_markdown.splitlines()

    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if idx == 1 and stripped == "---":
            in_frontmatter = True
            continue
        if in_frontmatter:
            if stripped == "---":
                in_frontmatter = False
            continue

        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue

        if not in_fence:
            match = _HEADING_RE.match(line)
            if match:
                level = len(match.group("hashes"))
                text = match.group("text").strip()
                # Strip inline markdown formatting markers from display text
                clean_text = re.sub(r"[*_`~]", "", text).strip() or text
                anchor_id = _slugify(clean_text, seen_slugs)
                headings.append(
                    HeadingNode(
                        level=level,
                        text=clean_text,
                        anchor_id=anchor_id,
                        line_number=idx,
                    )
                )
    return headings


def _wrap_code_lines(code: str, max_cols: int = 84) -> str:
    """Wrap overly long source code lines cleanly so code blocks never overflow horizontally on PDF pages."""
    wrapped_lines: list[str] = []
    for line in code.splitlines():
        expanded = line.expandtabs(4)
        if len(expanded) <= max_cols:
            wrapped_lines.append(expanded)
        else:
            # Preserve leading indentation on continuation lines
            indent_match = re.match(r"^(\s*)", expanded)
            indent = indent_match.group(1) if indent_match else ""
            subseq_indent = indent + "    " if len(indent) < max_cols // 2 else "    "
            chunks = textwrap.wrap(
                expanded,
                width=max_cols,
                subsequent_indent=subseq_indent,
                break_long_words=True,
                break_on_hyphens=False,
                replace_whitespace=False,
                drop_whitespace=False,
            )
            wrapped_lines.extend(chunks if chunks else [expanded])
    return "\n".join(wrapped_lines)


def _highlight_code_block(code: str, lang: str) -> str:
    """Render a fenced code block with Pygments inline styles (noclasses=True, style='friendly')."""
    wrapped_code = _wrap_code_lines(code, max_cols=84)
    lexer = None
    if lang:
        try:
            lexer = get_lexer_by_name(lang.strip().lower(), stripall=False)
        except ClassNotFound:
            lexer = None
    if lexer is None:
        try:
            lexer = guess_lexer(wrapped_code) if len(wrapped_code.strip()) > 20 else TextLexer()
        except ClassNotFound:
            lexer = TextLexer()

    formatter = HtmlFormatter(
        noclasses=True,
        style="friendly",
        nowrap=True,
    )
    highlighted_inner = highlight(wrapped_code, lexer, formatter).rstrip("\r\n")
    lang_badge = (
        f'<div style="font-family: Helvetica, sans-serif; font-size: 7.5pt; '
        f'color: #475569; font-weight: bold; text-transform: uppercase; '
        f'margin-bottom: 3pt;">{html.escape(lang.upper())}</div>'
        if lang
        else ""
    )
    return (
        f'<div class="code-container" style="background-color: #F1F5F9; '
        f'border: 1pt solid #CBD5E1; padding: 7pt 9pt; margin: 8pt 0 10pt 0;">'
        f"{lang_badge}"
        f'<pre style="margin: 0; padding: 0; border: none; background: transparent; '
        f'font-family: Courier, monospace; white-space: pre-wrap; word-wrap: break-word;">'
        f"<code>{highlighted_inner}</code></pre></div>"
    )


def _preprocess_fenced_code_with_pygments(markdown_body: str) -> tuple[str, dict[str, str]]:
    """Replace fenced code blocks with placeholders and return rendered Pygments HTML blocks."""
    placeholders: dict[str, str] = {}
    counter = 0

    def _replacer(match: re.Match[str]) -> str:
        nonlocal counter
        counter += 1
        lang = (match.group("lang") or "").strip()
        code = match.group("code")
        key = f"@@PYGMENTS_CODE_BLOCK_{counter}@@"
        placeholders[key] = _highlight_code_block(code, lang)
        return f"\n\n{key}\n\n"

    processed = _FENCED_CODE_RE.sub(_replacer, markdown_body)
    return processed, placeholders


def _build_toc_html(headings: list[HeadingNode]) -> str:
    """Build a clean, print-ready Table of Contents HTML block from extracted headings."""
    if not headings:
        return ""

    items_html: list[str] = []
    min_level = min(h.level for h in headings)
    for h in headings:
        if h.level > 4:
            continue
        indent_pt = max(0, (h.level - min_level) * 14)
        weight = "bold" if h.level == 1 else "normal"
        color = "#0F172A" if h.level == 1 else "#334155"
        escaped_text = html.escape(h.text)
        items_html.append(
            f'<div style="margin: 3pt 0 3pt {indent_pt}pt; font-weight: {weight}; color: {color};">'
            f'<a href="#{h.anchor_id}" style="text-decoration: none; color: {color};">'
            f"{escaped_text}</a></div>"
        )

    if not items_html:
        return ""

    return (
        '<div class="toc-container">'
        '<div class="toc-heading">Table of Contents</div>'
        + "".join(items_html)
        + "</div>"
    )


def compile_markdown(raw_text: str, base_dir: Optional[str] = None) -> CompiledManuscript:
    """Compile raw Markdown with YAML frontmatter, callouts, and Pygments code blocks into CompiledManuscript."""
    raw_input = raw_text or ""
    metadata, markdown_body = parse_frontmatter(raw_input)
    headings = _extract_headings(raw_input)

    # Calculate word count and estimated reading time (at 200 WPM) on the Markdown body
    words = _WORD_RE.findall(markdown_body)
    word_count = len(words)
    reading_time_min = max(1, math.ceil(word_count / 200)) if word_count > 0 else 0

    # Resolve relative image paths against base_dir
    resolved_body = resolve_markdown_image_paths(markdown_body, base_dir)

    # Extract and highlight fenced code blocks first so inner `> [!NOTE]` or Markdown inside code isn't altered
    code_tokenized_body, code_placeholders = _preprocess_fenced_code_with_pygments(resolved_body)

    # Transform GitHub/Obsidian callouts into semantic HTML containers
    callout_processed_body = preprocess_callouts(code_tokenized_body)

    # Convert remaining Markdown to HTML
    md_engine = markdown.Markdown(
        extensions=["tables", "fenced_code", "toc", "sane_lists", "attr_list"]
    )
    body_html = md_engine.convert(callout_processed_body)

    # Restore Pygments highlighted code blocks (cleaning up wrapping <p> tags if Markdown added them)
    for key, highlighted_html in code_placeholders.items():
        body_html = body_html.replace(f"<p>{key}</p>", highlighted_html)
        body_html = body_html.replace(key, highlighted_html)

    toc_html = _build_toc_html(headings)

    return CompiledManuscript(
        metadata=metadata,
        raw_markdown=raw_input,
        body_html=body_html,
        toc_html=toc_html,
        headings=headings,
        word_count=word_count,
        reading_time_min=reading_time_min,
    )
