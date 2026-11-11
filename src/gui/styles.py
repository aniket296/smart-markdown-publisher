"""Slate-Teal desktop publishing theme and TTK style definitions."""

import tkinter as tk
from tkinter import ttk

# Color Palette Constants
SLATE_HEADER = "#0F172A"
SLATE_SIDEBAR = "#1E293B"
SLATE_CANVAS = "#334155"
SLATE_BORDER = "#CBD5E1"
SLATE_MUTED = "#64748B"

TEAL_PRIMARY = "#0D9488"
TEAL_HOVER = "#0F766E"
TEAL_LIGHT = "#F0FDFA"

WORKSPACE_BG = "#F8FAFC"
SURFACE_WHITE = "#FFFFFF"
TEXT_PRIMARY = "#1E293B"
TEXT_INVERSE = "#F8FAFC"

# Typography Constants
FONT_UI = ("Segoe UI", 9)
FONT_UI_BOLD = ("Segoe UI", 9, "bold")
FONT_HEADER = ("Segoe UI", 11, "bold")
FONT_SMALL = ("Segoe UI", 8)
FONT_EDITOR = ("Consolas", 11)
FONT_EDITOR_BOLD = ("Consolas", 11, "bold")


def apply_studio_theme(root: tk.Misc) -> ttk.Style:
    """Configure the Slate-Teal TTK "clam" theme on the root window."""
    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")

    style.configure(
        ".",
        background=WORKSPACE_BG,
        foreground=TEXT_PRIMARY,
        font=FONT_UI,
    )

    style.configure("Studio.TFrame", background=WORKSPACE_BG)
    style.configure("Toolbar.TFrame", background=SLATE_HEADER)
    style.configure("Surface.TFrame", background=SURFACE_WHITE)
    style.configure("StatusBar.TFrame", background=SLATE_SIDEBAR)

    style.configure(
        "ToolbarTitle.TLabel",
        background=SLATE_HEADER,
        foreground=TEXT_INVERSE,
        font=FONT_HEADER,
    )
    style.configure(
        "ToolbarGroup.TLabel",
        background=SLATE_HEADER,
        foreground="#94A3B8",
        font=FONT_UI_BOLD,
    )
    style.configure(
        "StatusBar.TLabel",
        background=SLATE_SIDEBAR,
        foreground="#E2E8F0",
        font=FONT_SMALL,
    )
    style.configure(
        "SectionHeader.TLabel",
        background=WORKSPACE_BG,
        foreground=TEXT_PRIMARY,
        font=FONT_UI_BOLD,
    )

    # Standard Toolbar Button
    style.configure(
        "Toolbar.TButton",
        background="#1E293B",
        foreground=TEXT_INVERSE,
        bordercolor="#334155",
        lightcolor="#1E293B",
        darkcolor="#1E293B",
        font=FONT_UI,
        padding=(8, 4),
    )
    style.map(
        "Toolbar.TButton",
        background=[("active", "#334155"), ("pressed", "#0F172A")],
        foreground=[("active", "#FFFFFF")],
    )

    # Prominent Primary Accent Export Button
    style.configure(
        "Accent.TButton",
        background=TEAL_PRIMARY,
        foreground="#FFFFFF",
        bordercolor=TEAL_PRIMARY,
        lightcolor=TEAL_PRIMARY,
        darkcolor=TEAL_HOVER,
        font=FONT_UI_BOLD,
        padding=(12, 5),
    )
    style.map(
        "Accent.TButton",
        background=[("active", TEAL_HOVER), ("pressed", "#115E59")],
        foreground=[("active", "#FFFFFF")],
    )

    # Secondary Studio Action Button
    style.configure(
        "Secondary.TButton",
        background=SURFACE_WHITE,
        foreground=TEXT_PRIMARY,
        bordercolor=SLATE_BORDER,
        font=FONT_UI,
        padding=(7, 3),
    )
    style.map(
        "Secondary.TButton",
        background=[("active", "#E2E8F0")],
    )

    # Notebook & Treeview styling for Outline Sidebar
    style.configure(
        "Studio.TNotebook",
        background=WORKSPACE_BG,
        borderwidth=0,
    )
    style.configure(
        "Studio.TNotebook.Tab",
        background="#E2E8F0",
        foreground=TEXT_PRIMARY,
        font=FONT_UI_BOLD,
        padding=(10, 5),
    )
    style.map(
        "Studio.TNotebook.Tab",
        background=[("selected", SURFACE_WHITE)],
        foreground=[("selected", TEAL_PRIMARY)],
    )

    style.configure(
        "Outline.Treeview",
        background=SURFACE_WHITE,
        fieldbackground=SURFACE_WHITE,
        foreground=TEXT_PRIMARY,
        rowheight=26,
        font=FONT_UI,
        borderwidth=0,
    )
    style.map(
        "Outline.Treeview",
        background=[("selected", TEAL_LIGHT)],
        foreground=[("selected", TEAL_HOVER)],
    )

    style.configure(
        "Toolbar.TCombobox",
        fieldbackground=SURFACE_WHITE,
        background=SURFACE_WHITE,
        foreground=TEXT_PRIMARY,
        padding=3,
    )

    return style
