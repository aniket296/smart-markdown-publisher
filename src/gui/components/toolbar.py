"""Top publishing toolbar with File, Insert, Typesetting Profile, and Export controls."""

import tkinter as tk
from tkinter import ttk
from typing import Callable

from src.gui.styles import FONT_UI, SLATE_HEADER
from src.models.print_profile import MarginPreset, PageSize, PrintProfile, ThemeId


class PublishingToolbar(ttk.Frame):
    """Top studio toolbar providing file operations, Markdown snippet insertion, and print profile controls."""

    THEME_DISPLAY_MAP = {
        "Academic": ThemeId.ACADEMIC,
        "Technical": ThemeId.TECHNICAL,
        "Executive": ThemeId.EXECUTIVE,
        "Compact": ThemeId.COMPACT,
    }
    THEME_REVERSE_MAP = {v: k for k, v in THEME_DISPLAY_MAP.items()}

    PAGE_DISPLAY_MAP = {
        "A4": PageSize.A4,
        "Letter": PageSize.LETTER,
    }
    PAGE_REVERSE_MAP = {v: k for k, v in PAGE_DISPLAY_MAP.items()}

    MARGIN_DISPLAY_MAP = {
        "Standard": MarginPreset.STANDARD,
        "Wide": MarginPreset.WIDE,
        "Narrow": MarginPreset.NARROW,
    }
    MARGIN_REVERSE_MAP = {v: k for k, v in MARGIN_DISPLAY_MAP.items()}

    def __init__(
        self,
        parent: tk.Misc,
        initial_profile: PrintProfile | None = None,
        on_action: Callable[[str], None] | None = None,
        on_profile_change: Callable[[PrintProfile], None] | None = None,
    ) -> None:
        super().__init__(parent, style="Toolbar.TFrame", padding=(10, 6))
        self._profile = initial_profile or PrintProfile()
        self._on_action = on_action
        self._on_profile_change = on_profile_change

        self.theme_var = tk.StringVar(
            value=self.THEME_REVERSE_MAP.get(self._profile.theme, "Technical")
        )
        self.page_size_var = tk.StringVar(
            value=self.PAGE_REVERSE_MAP.get(self._profile.page_size, "A4")
        )
        self.margin_var = tk.StringVar(
            value=self.MARGIN_REVERSE_MAP.get(self._profile.margins, "Standard")
        )
        self.font_size_var = tk.IntVar(value=self._profile.base_font_size)

        self._build_ui()

    def _build_ui(self) -> None:
        # Row 1: File & Insert Snippet Actions + Primary Export PDF CTA
        top_row = ttk.Frame(self, style="Toolbar.TFrame")
        top_row.pack(fill=tk.X, expand=True, pady=(0, 4))

        # File Group
        ttk.Label(top_row, text="FILE:", style="ToolbarGroup.TLabel").pack(
            side=tk.LEFT, padx=(0, 4)
        )
        self._add_btn(top_row, "New Sample", "new_sample")
        self._add_btn(top_row, "Open .md", "open_md")
        self._add_btn(top_row, "Save .md", "save_md")
        self._add_btn(top_row, "Bind Folder as Book...", "bind_folder")

        self._add_divider(top_row)

        # Insert Group
        ttk.Label(top_row, text="INSERT:", style="ToolbarGroup.TLabel").pack(
            side=tk.LEFT, padx=(0, 4)
        )
        self._add_btn(top_row, "YAML Header", "insert_yaml")
        self._add_btn(top_row, "Bold", "insert_bold")
        self._add_btn(top_row, "Code Block", "insert_code")
        self._add_btn(top_row, "Table", "insert_table")
        self._add_btn(top_row, "Callout [!NOTE]", "insert_callout")

        # Publish CTA on Right
        export_btn = ttk.Button(
            top_row,
            text="Export Typeset PDF",
            style="Accent.TButton",
            command=lambda: self._trigger_action("export_pdf"),
        )
        export_btn.pack(side=tk.RIGHT, padx=(8, 0))

        # Row 2: Typesetting Profile Controls
        bottom_row = ttk.Frame(self, style="Toolbar.TFrame")
        bottom_row.pack(fill=tk.X, expand=True)

        ttk.Label(
            bottom_row, text="TYPESETTING PROFILE:", style="ToolbarGroup.TLabel"
        ).pack(side=tk.LEFT, padx=(0, 6))

        # Theme Combobox
        ttk.Label(bottom_row, text="Theme:", style="ToolbarGroup.TLabel").pack(
            side=tk.LEFT, padx=(4, 3)
        )
        self.theme_combo = ttk.Combobox(
            bottom_row,
            textvariable=self.theme_var,
            values=list(self.THEME_DISPLAY_MAP.keys()),
            state="readonly",
            width=11,
            style="Toolbar.TCombobox",
        )
        self.theme_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.theme_combo.bind("<<ComboboxSelected>>", self._handle_profile_changed)

        # Page Size Combobox
        ttk.Label(bottom_row, text="Page Size:", style="ToolbarGroup.TLabel").pack(
            side=tk.LEFT, padx=(4, 3)
        )
        self.page_combo = ttk.Combobox(
            bottom_row,
            textvariable=self.page_size_var,
            values=list(self.PAGE_DISPLAY_MAP.keys()),
            state="readonly",
            width=8,
            style="Toolbar.TCombobox",
        )
        self.page_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.page_combo.bind("<<ComboboxSelected>>", self._handle_profile_changed)

        # Margin Combobox
        ttk.Label(bottom_row, text="Margins:", style="ToolbarGroup.TLabel").pack(
            side=tk.LEFT, padx=(4, 3)
        )
        self.margin_combo = ttk.Combobox(
            bottom_row,
            textvariable=self.margin_var,
            values=list(self.MARGIN_DISPLAY_MAP.keys()),
            state="readonly",
            width=10,
            style="Toolbar.TCombobox",
        )
        self.margin_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.margin_combo.bind("<<ComboboxSelected>>", self._handle_profile_changed)

        # Font Size Spinner (9 to 14)
        ttk.Label(bottom_row, text="Font Size (pt):", style="ToolbarGroup.TLabel").pack(
            side=tk.LEFT, padx=(4, 3)
        )
        self.font_spin = tk.Spinbox(
            bottom_row,
            from_=9,
            to=14,
            textvariable=self.font_size_var,
            width=4,
            font=FONT_UI,
            bg="#FFFFFF",
            fg="#0F172A",
            relief=tk.FLAT,
            command=self._handle_profile_changed,
        )
        self.font_spin.pack(side=tk.LEFT, padx=(0, 6))
        self.font_spin.bind("<Return>", self._handle_profile_changed)
        self.font_spin.bind("<FocusOut>", self._handle_profile_changed)

    def _add_btn(self, parent: ttk.Frame, label: str, action_id: str) -> ttk.Button:
        btn = ttk.Button(
            parent,
            text=label,
            style="Toolbar.TButton",
            command=lambda: self._trigger_action(action_id),
        )
        btn.pack(side=tk.LEFT, padx=2)
        return btn

    def _add_divider(self, parent: ttk.Frame) -> None:
        div = tk.Frame(parent, width=1, height=20, bg="#334155")
        div.pack(side=tk.LEFT, padx=8, pady=2)

    def _trigger_action(self, action_id: str) -> None:
        if self._on_action is not None:
            self._on_action(action_id)

    def _handle_profile_changed(self, _event: object = None) -> None:
        theme = self.THEME_DISPLAY_MAP.get(self.theme_var.get(), ThemeId.TECHNICAL)
        page_size = self.PAGE_DISPLAY_MAP.get(self.page_size_var.get(), PageSize.A4)
        margins = self.MARGIN_DISPLAY_MAP.get(
            self.margin_var.get(), MarginPreset.STANDARD
        )
        try:
            font_sz = max(9, min(int(self.font_size_var.get()), 14))
        except (ValueError, tk.TclError):
            font_sz = 11
            self.font_size_var.set(11)

        self._profile.theme = theme
        self._profile.page_size = page_size
        self._profile.margins = margins
        self._profile.base_font_size = font_sz

        if self._on_profile_change is not None:
            self._on_profile_change(self._profile)

    def get_profile(self) -> PrintProfile:
        """Return the current PrintProfile state."""
        return self._profile
