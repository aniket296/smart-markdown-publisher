"""YAML frontmatter parser with graceful fallback to first H1 heading."""

import re
from typing import Any
import yaml
from src.models.document_model import DocumentMetadata

# Matches a leading YAML frontmatter block delimited by --- on line 1
_FRONTMATTER_PATTERN = re.compile(
    r"\A\ufeff?---[ \t]*\r?\n(?P<yaml>.*?)\r?\n---[ \t]*(?:\r?\n|\Z)",
    re.DOTALL,
)

# Matches the first # H1 heading in the Markdown body
_FIRST_H1_PATTERN = re.compile(r"^[ \t]*#[ \t]+(?P<title>[^\r\n#]+?)[ \t#]*$", re.MULTILINE)


def _to_bool(value: Any, default: bool = False) -> bool:
    """Coerce YAML value into a boolean safely."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        lower = value.strip().lower()
        if lower in {"true", "yes", "1", "on", "enabled"}:
            return True
        if lower in {"false", "no", "0", "off", "disabled"}:
            return False
    return default


def _to_str(value: Any, default: str = "") -> str:
    """Coerce YAML value into a clean string safely."""
    if value is None:
        return default
    if isinstance(value, list):
        return ", ".join(str(item).strip() for item in value if item is not None)
    return str(value).strip()


def _extract_first_h1(markdown_body: str) -> str:
    """Extract the text of the first # H1 heading outside fenced code blocks."""
    in_fence = False
    for line in markdown_body.splitlines():
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if not in_fence:
            match = _FIRST_H1_PATTERN.match(line)
            if match:
                return match.group("title").strip()
    return "Untitled Document"


def parse_frontmatter(raw_text: str) -> tuple[DocumentMetadata, str]:
    """Parse leading YAML frontmatter from raw_text and return (DocumentMetadata, markdown_body).

    Gracefully handles missing or malformed YAML without crashing, falling back to the
    first # H1 heading as the document title if no YAML title is provided.
    """
    if not raw_text:
        return DocumentMetadata(), ""

    match = _FRONTMATTER_PATTERN.match(raw_text)
    yaml_data: dict[str, Any] = {}
    body = raw_text

    if match:
        raw_yaml = match.group("yaml")
        candidate_body = raw_text[match.end() :]
        try:
            loaded = yaml.safe_load(raw_yaml)
            if isinstance(loaded, dict):
                yaml_data = {str(k).strip().lower(): v for k, v in loaded.items()}
                body = candidate_body
            elif loaded is None:
                body = candidate_body
        except yaml.YAMLError:
            # Malformed YAML: still strip the broken frontmatter fence if clearly intended,
            # or fall back safely without raising an exception.
            body = candidate_body

    fallback_title = _extract_first_h1(body)
    title = _to_str(yaml_data.get("title"), default="") or fallback_title

    subtitle = _to_str(yaml_data.get("subtitle"), default="")
    author = _to_str(yaml_data.get("author") or yaml_data.get("authors"), default="")
    date = _to_str(yaml_data.get("date"), default="")
    version = _to_str(yaml_data.get("version"), default="")
    institution = _to_str(
        yaml_data.get("institution") or yaml_data.get("organization"), default=""
    )

    include_cover = _to_bool(
        yaml_data.get(
            "include_cover",
            yaml_data.get("cover", False),
        ),
        default=False,
    )
    include_toc = _to_bool(
        yaml_data.get(
            "include_toc",
            yaml_data.get("toc", False),
        ),
        default=False,
    )

    header_text = _to_str(
        yaml_data.get("header_text", yaml_data.get("header", "")), default=""
    )
    footer_text = _to_str(
        yaml_data.get("footer_text", yaml_data.get("footer", "")), default=""
    )

    metadata = DocumentMetadata(
        title=title,
        subtitle=subtitle,
        author=author,
        date=date,
        version=version,
        institution=institution,
        include_cover=include_cover,
        include_toc=include_toc,
        header_text=header_text,
        footer_text=footer_text,
    )
    return metadata, body
