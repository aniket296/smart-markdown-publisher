"""GitHub / Obsidian admonition callout preprocessor (`> [!NOTE]`, `> [!WARNING]`, etc.)."""

import html
import re
import markdown

_SUPPORTED_CALLOUTS = {"NOTE", "TIP", "IMPORTANT", "WARNING", "CAUTION"}

# Matches `> [!TYPE]` or `> [!TYPE] Custom Title`
_CALLOUT_HEADER_RE = re.compile(
    r"^[ \t]*>[ \t]*\[!(?P<kind>NOTE|TIP|IMPORTANT|WARNING|CAUTION)\](?:[ \t]+(?P<custom_title>[^\r\n]+))?[ \t]*$",
    re.IGNORECASE,
)

# Matches subsequent blockquote continuation lines `> ...`
_BLOCKQUOTE_LINE_RE = re.compile(r"^[ \t]*>[ \t]?(?P<content>.*)$")


def _render_inner_markdown(lines: list[str]) -> str:
    """Convert inner callout Markdown lines into clean HTML paragraphs/lists."""
    raw_inner = "\n".join(lines).strip()
    if not raw_inner:
        return ""
    return markdown.markdown(
        raw_inner,
        extensions=["tables", "fenced_code", "sane_lists"],
    )


def preprocess_callouts(markdown_body: str) -> str:
    """Detect GitHub/Obsidian-style blockquote callouts and transform them into semantic HTML containers.

    Supported callouts: `> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!WARNING]`, `> [!CAUTION]`.
    Produces `<div class="callout callout-note"><p class="callout-title">NOTE</p>...</div>`.
    """
    if not markdown_body:
        return ""

    lines = markdown_body.splitlines()
    output_lines: list[str] = []
    idx = 0
    total = len(lines)
    in_fence = False

    while idx < total:
        line = lines[idx]
        stripped = line.strip()

        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            output_lines.append(line)
            idx += 1
            continue

        if not in_fence:
            header_match = _CALLOUT_HEADER_RE.match(line)
            if header_match:
                kind = header_match.group("kind").upper()
                if kind in _SUPPORTED_CALLOUTS:
                    custom_title = (header_match.group("custom_title") or "").strip()
                    display_title = html.escape(custom_title if custom_title else kind)
                    kind_slug = kind.lower()

                    idx += 1
                    inner_lines: list[str] = []
                    while idx < total:
                        cont_match = _BLOCKQUOTE_LINE_RE.match(lines[idx])
                        if not cont_match:
                            break
                        # Stop if a brand-new callout starts immediately inside the blockquote
                        if _CALLOUT_HEADER_RE.match(lines[idx]):
                            break
                        inner_lines.append(cont_match.group("content"))
                        idx += 1

                    inner_html = _render_inner_markdown(inner_lines)
                    block_html = (
                        f'<div class="callout callout-{kind_slug}">'
                        f'<p class="callout-title">{display_title}</p>'
                        f"{inner_html}"
                        f"</div>"
                    )
                    output_lines.append("")
                    output_lines.append(block_html)
                    output_lines.append("")
                    continue

        output_lines.append(line)
        idx += 1

    return "\n".join(output_lines)
