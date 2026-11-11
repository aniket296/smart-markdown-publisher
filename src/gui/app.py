"""Main Desktop Publishing Studio Shell."""

import ctypes
from pathlib import Path
import sys
import tkinter as tk
from tkinter import ttk

from src.gui.components.toolbar import PublishingToolbar
from src.gui.styles import WORKSPACE_BG, apply_studio_theme
from src.models.print_profile import PrintProfile
from src.utils.config import get_default_page_size, get_default_theme
from src.utils.logger import get_logger

logger = get_logger("gui.app")


def enable_windows_high_dpi() -> None:
    """Enable Windows Per-Monitor High-DPI awareness."""
    if sys.platform == "win32":
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass


def resolve_app_icon_path() -> Path:
    """Resolve the path to assets/app_icon.ico in both source and PyInstaller frozen modes."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = Path(getattr(sys, "_MEIPASS"))
    else:
        base = Path(__file__).resolve().parent.parent.parent
    return base / "assets" / "app_icon.ico"


class SmartMarkdownPublisherApp:
    """Primary Tkinter/TTK desktop application controller."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Smart Markdown-to-Print Desktop Publisher")
        self.root.geometry("1420x880")
        self.root.minsize(1024, 660)
        self.root.configure(bg=WORKSPACE_BG)

        icon_path = resolve_app_icon_path()
        if icon_path.is_file():
            try:
                self.root.iconbitmap(default=str(icon_path))
            except tk.TclError:
                pass

        self.style = apply_studio_theme(self.root)
        self.profile = PrintProfile(
            page_size=get_default_page_size(),
            theme=get_default_theme(),
        )

        self.toolbar = PublishingToolbar(
            self.root,
            initial_profile=self.profile,
            on_action=self._on_toolbar_action,
            on_profile_change=self._on_profile_changed,
        )
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        self.workspace_container = ttk.Frame(self.root, style="Studio.TFrame")
        self.workspace_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def _on_toolbar_action(self, action_id: str) -> None:
        logger.info("Toolbar action triggered: %s", action_id)

    def _on_profile_changed(self, profile: PrintProfile) -> None:
        self.profile = profile
        logger.info("Typesetting profile updated: %s", profile)
