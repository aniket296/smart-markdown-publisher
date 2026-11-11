"""Relative image path resolver for Markdown and embedded HTML images."""

import re
from pathlib import Path
from typing import Optional

_REMOTE_OR_DATA_PREFIXES = ("http://", "https://", "data:", "file://")

# Matches ![alt](path) or ![alt](path "title")
_MD_IMAGE_PATTERN = re.compile(
    r"!\[(?P<alt>[^\]]*)\]\(\s*(?P<path><[^>]+>|[^)\s\"']+)(?P<title>\s+[\"'][^\"']*[\"'])?\s*\)"
)

# Matches <img ... src="path" ...> or <img ... src='path' ...>
_HTML_IMG_PATTERN = re.compile(
    r"(<img\b[^>]*?\bsrc\s*=\s*)(?P<quote>[\"'])(?P<path>[^\"']+)(?P=quote)",
    re.IGNORECASE,
)


def _is_remote_or_absolute(raw_path: str) -> bool:
    """Return True if raw_path is an external URL, data URI, or already an absolute path."""
    lower = raw_path.strip().lower()
    if lower.startswith(_REMOTE_OR_DATA_PREFIXES):
        return True
    p = Path(raw_path.strip())
    return p.is_absolute()


def _resolve_single_path(raw_path: str, base_path: Path) -> str:
    """Resolve a single relative image path against base_path into a normalized forward-slash path."""
    cleaned = raw_path.strip()
    has_angle_brackets = cleaned.startswith("<") and cleaned.endswith(">")
    if has_angle_brackets:
        cleaned = cleaned[1:-1].strip()

    if not cleaned or _is_remote_or_absolute(cleaned):
        return raw_path

    resolved = (base_path / cleaned).resolve()
    normalized = resolved.as_posix()
    if has_angle_brackets:
        return f"<{normalized}>"
    return normalized


def resolve_markdown_image_paths(markdown_text: str, base_dir: Optional[str]) -> str:
    """Resolve relative Markdown ![alt](path) and HTML <img src="path"> image links against base_dir.

    Leaves http://, https://, data: URIs, and already-absolute paths untouched.
    """
    if not markdown_text or not base_dir:
        return markdown_text

    base_path = Path(base_dir).resolve()

    def _replace_md_image(match: re.Match[str]) -> str:
        alt = match.group("alt")
        raw_path = match.group("path")
        title = match.group("title") or ""
        new_path = _resolve_single_path(raw_path, base_path)
        return f"![{alt}]({new_path}{title})"

    def _replace_html_img(match: re.Match[str]) -> str:
        prefix = match.group(1)
        quote = match.group("quote")
        raw_path = match.group("path")
        new_path = _resolve_single_path(raw_path, base_path)
        return f"{prefix}{quote}{new_path}{quote}"

    updated = _MD_IMAGE_PATTERN.sub(_replace_md_image, markdown_text)
    updated = _HTML_IMG_PATTERN.sub(_replace_html_img, updated)
    return updated
