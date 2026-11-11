"""Print typesetting profiles, page dimensions, themes, and margin presets."""

from dataclasses import dataclass
from enum import Enum


class PageSize(Enum):
    """Standard print page sizes in PDF points (1 pt = 1/72 inch)."""

    A4 = (595, 842)
    LETTER = (612, 792)

    @property
    def width(self) -> int:
        return self.value[0]

    @property
    def height(self) -> int:
        return self.value[1]


class ThemeId(Enum):
    """Curated print typography themes."""

    ACADEMIC = "ACADEMIC"
    TECHNICAL = "TECHNICAL"
    EXECUTIVE = "EXECUTIVE"
    COMPACT = "COMPACT"


class MarginPreset(Enum):
    """Page margin presets in PDF points."""

    STANDARD = 54
    WIDE = 72
    NARROW = 36

    @property
    def points(self) -> int:
        return int(self.value)


@dataclass
class PrintProfile:
    """Configuration profile controlling PDF page layout and typography."""

    page_size: PageSize = PageSize.A4
    theme: ThemeId = ThemeId.TECHNICAL
    margins: MarginPreset = MarginPreset.STANDARD
    show_page_numbers: bool = True
    show_running_header: bool = True
    base_font_size: int = 11
