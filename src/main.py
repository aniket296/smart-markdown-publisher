"""Entrypoint for Smart Markdown-to-Print Desktop Publisher."""

import tkinter as tk
from src.gui.app import SmartMarkdownPublisherApp, enable_windows_high_dpi
from src.utils.logger import get_logger


def main() -> None:
    """Initialize High-DPI awareness and launch the desktop publishing studio."""
    enable_windows_high_dpi()
    logger = get_logger("main")
    logger.info("Starting Smart Markdown-to-Print Desktop Publisher v1.0.0")

    root = tk.Tk()
    _app = SmartMarkdownPublisherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
