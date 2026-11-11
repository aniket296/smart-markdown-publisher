"""Strongly-typed domain models for Markdown documents and compiled manuscripts."""

from dataclasses import dataclass, field


@dataclass
class DocumentMetadata:
    """YAML frontmatter and document-level publishing metadata."""

    title: str = "Untitled Document"
    subtitle: str = ""
    author: str = ""
    date: str = ""
    version: str = ""
    institution: str = ""
    include_cover: bool = False
    include_toc: bool = False
    header_text: str = ""
    footer_text: str = ""


@dataclass
class HeadingNode:
    """Represents a heading in the Markdown document for outline navigation and PDF bookmarks."""

    level: int
    text: str
    anchor_id: str
    line_number: int

    def __post_init__(self) -> None:
        if not 1 <= self.level <= 6:
            raise ValueError(f"Heading level must be between 1 and 6, got {self.level}")


@dataclass
class CompiledManuscript:
    """Compiled Markdown manuscript ready for print typesetting."""

    metadata: DocumentMetadata
    raw_markdown: str
    body_html: str
    toc_html: str
    headings: list[HeadingNode] = field(default_factory=list)
    word_count: int = 0
    reading_time_min: int = 1
