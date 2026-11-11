"""Environment configuration loader with safe typed getters."""

import os
from pathlib import Path
from dotenv import load_dotenv
from src.models.print_profile import PageSize, ThemeId

# Load .env from project root if present
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_PROJECT_ROOT / ".env", override=False)


def get_app_log_level() -> str:
    """Return configured log level (default: INFO)."""
    level = os.getenv("APP_LOG_LEVEL", "INFO").strip().upper()
    if level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        return "INFO"
    return level


def get_default_theme() -> ThemeId:
    """Return configured default print theme (default: ThemeId.TECHNICAL)."""
    raw = os.getenv("DEFAULT_THEME", "TECHNICAL").strip().upper()
    try:
        return ThemeId[raw]
    except KeyError:
        return ThemeId.TECHNICAL


def get_default_page_size() -> PageSize:
    """Return configured default page size (default: PageSize.A4)."""
    raw = os.getenv("DEFAULT_PAGE_SIZE", "A4").strip().upper()
    try:
        return PageSize[raw]
    except KeyError:
        return PageSize.A4


def get_preview_debounce_ms() -> int:
    """Return configured editor-to-PDF preview debounce delay in milliseconds (default: 350)."""
    raw = os.getenv("PREVIEW_DEBOUNCE_MS", "350").strip()
    try:
        val = int(raw)
        return max(50, min(val, 5000))
    except ValueError:
        return 350
