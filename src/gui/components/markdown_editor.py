"""Line-numbered Markdown editor with syntax highlighting, snippet helpers, and live metrics bar."""

import math
import re
import tkinter as tk
from tkinter import ttk
from typing import Callable

from src.gui.styles import (
    FONT_EDITOR,
    FONT_EDITOR_BOLD,
    FONT_SMALL,
    SLATE_SIDEBAR,
    SURFACE_WHITE,
    TEAL_PRIMARY,
    TEXT_PRIMARY,
)

_WORD_RE = re.compile(r"\b[\w'-]+\b", re.UNICODE)
_BOLD_RE = re.compile(r"\*\*[^*\n]+\*\*")
_INLINE_CODE_RE = re.compile(r"`[^`\n]+`")


class MarkdownEditorPane(ttk.Frame):
    """Composite Markdown editor featuring a synchronized line-number gutter, syntax highlighting, and metrics bar."""

    def __init__(
        self,
        parent: tk.Misc,
        debounce_ms: int = 350,
        on_debounced_change: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__(parent, style="Surface.TFrame")
        self._debounce_ms = debounce_ms
        self._on_debounced_change = on_debounced_change
        self._debounce_after_id: str | None = None
        self._suppress_change_event = False

        self.metrics_var = tk.StringVar(
            value="Words: 0 | Est. Reading Time: 0 min | Line: 1, Col: 1"
        )

        self._build_ui()
        self._configure_tags()
        self._bind_events()

    def _build_ui(self) -> None:
        # Top section header bar
        header_bar = ttk.Frame(self, style="Studio.TFrame", padding=(8, 4))
        header_bar.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(
            header_bar,
            text="MARKDOWN MANUSCRIPT EDITOR",
            style="SectionHeader.TLabel",
        ).pack(side=tk.LEFT)

        # Main editor area (Line-number Canvas + Text + Vertical Scrollbar)
        editor_body = ttk.Frame(self, style="Surface.TFrame")
        editor_body.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.gutter = tk.Canvas(
            editor_body,
            width=48,
            bg="#F1F5F9",
            highlightthickness=0,
            bd=0,
        )
        self.gutter.pack(side=tk.LEFT, fill=tk.Y)

        self.v_scroll = ttk.Scrollbar(
            editor_body, orient=tk.VERTICAL, command=self._on_scrollbar_scroll
        )
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.text = tk.Text(
            editor_body,
            wrap=tk.WORD,
            undo=True,
            maxundo=-1,
            font=FONT_EDITOR,
            bg=SURFACE_WHITE,
            fg=TEXT_PRIMARY,
            insertbackground=TEAL_PRIMARY,
            selectbackground="#CCFBF1",
            selectforeground=TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=12,
            pady=8,
            spacing1=2,
            spacing3=2,
            yscrollcommand=self._on_text_yscroll,
        )
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Bottom live metrics status bar
        status_frame = tk.Frame(self, bg=SLATE_SIDEBAR, padx=10, pady=4)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.metrics_label = tk.Label(
            status_frame,
            textvariable=self.metrics_var,
            bg=SLATE_SIDEBAR,
            fg="#E2E8F0",
            font=FONT_SMALL,
            anchor=tk.W,
        )
        self.metrics_label.pack(side=tk.LEFT, fill=tk.X)

    def _configure_tags(self) -> None:
        self.text.tag_configure(
            "yaml_frontmatter",
            foreground="#0369A1",
            background="#F0F9FF",
        )
        self.text.tag_configure(
            "heading",
            foreground="#0F766E",
            font=FONT_EDITOR_BOLD,
        )
        self.text.tag_configure(
            "code_fence",
            foreground="#475569",
            background="#F1F5F9",
        )
        self.text.tag_configure(
            "inline_code",
            foreground="#B45309",
            background="#FEF3C7",
        )
        self.text.tag_configure(
            "callout",
            foreground="#6D28D9",
            background="#F5F3FF",
            font=FONT_EDITOR_BOLD,
        )
        self.text.tag_configure(
            "bold_span",
            foreground="#0F172A",
            font=FONT_EDITOR_BOLD,
        )
        self.text.tag_configure(
            "outline_flash",
            background="#99F6E4",
        )

    def _bind_events(self) -> None:
        self.text.bind("<<Modified>>", self._on_text_modified)
        self.text.bind("<KeyRelease>", self._on_cursor_or_view_change)
        self.text.bind("<ButtonRelease-1>", self._on_cursor_or_view_change)
        self.text.bind("<MouseWheel>", self._on_mousewheel)
        self.text.bind("<Configure>", lambda _e: self.redraw_line_numbers())

    def _on_scrollbar_scroll(self, *args: object) -> None:
        self.text.yview(*args)
        self.redraw_line_numbers()

    def _on_text_yscroll(self, first: str, last: str) -> None:
        self.v_scroll.set(first, last)
        self.redraw_line_numbers()

    def _on_mousewheel(self, _event: tk.Event) -> None:
        self.after_idle(self.redraw_line_numbers)

    def _on_cursor_or_view_change(self, _event: object = None) -> None:
        self.update_metrics()
        self.redraw_line_numbers()

    def _on_text_modified(self, _event: object = None) -> None:
        if not self.text.edit_modified():
            return
        self.text.edit_modified(False)
        self.apply_syntax_highlighting()
        self.update_metrics()
        self.redraw_line_numbers()

        if not self._suppress_change_event:
            self._schedule_debounced_callback()

    def _schedule_debounced_callback(self) -> None:
        if self._debounce_after_id is not None:
            try:
                self.after_cancel(self._debounce_after_id)
            except ValueError:
                pass
        self._debounce_after_id = self.after(
            self._debounce_ms, self._fire_debounced_callback
        )

    def _fire_debounced_callback(self) -> None:
        self._debounce_after_id = None
        if self._on_debounced_change is not None:
            self._on_debounced_change(self.get_text())

    def redraw_line_numbers(self) -> None:
        """Synchronize the vertical line-number gutter canvas with visible editor lines."""
        self.gutter.delete("all")
        i = self.text.index("@0,0")
        while True:
            dline = self.text.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            line_num = str(i).split(".")[0]
            self.gutter.create_text(
                40,
                y + 2,
                anchor=tk.NE,
                text=line_num,
                font=FONT_SMALL,
                fill="#64748B",
            )
            i = self.text.index(f"{i}+1line")

    def update_metrics(self) -> None:
        """Compute live word count, reading time (200 WPM), and cursor Line/Col."""
        content = self.get_text()
        word_count = len(_WORD_RE.findall(content))
        reading_min = max(1, math.ceil(word_count / 200)) if word_count > 0 else 0

        cursor_index = self.text.index(tk.INSERT)
        line_str, col_str = cursor_index.split(".")
        line_num = int(line_str)
        col_num = int(col_str) + 1

        self.metrics_var.set(
            f"Words: {word_count} | Est. Reading Time: {reading_min} min | Line: {line_num}, Col: {col_num}"
        )

    def apply_syntax_highlighting(self) -> None:
        """Apply lightweight tag highlighting for YAML frontmatter, headings, code fences, callouts, and bold spans."""
        for tag in (
            "yaml_frontmatter",
            "heading",
            "code_fence",
            "inline_code",
            "callout",
            "bold_span",
        ):
            self.text.tag_remove(tag, "1.0", tk.END)

        lines = self.get_text().splitlines()
        in_yaml = False
        in_fence = False

        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            line_start = f"{idx}.0"
            line_end = f"{idx}.end"

            if idx == 1 and stripped == "---":
                in_yaml = True
                self.text.tag_add("yaml_frontmatter", line_start, line_end)
                continue

            if in_yaml:
                self.text.tag_add("yaml_frontmatter", line_start, line_end)
                if stripped == "---":
                    in_yaml = False
                continue

            if stripped.startswith("```") or stripped.startswith("~~~"):
                self.text.tag_add("code_fence", line_start, line_end)
                in_fence = not in_fence
                continue

            if in_fence:
                self.text.tag_add("code_fence", line_start, line_end)
                continue

            if stripped.startswith("#"):
                self.text.tag_add("heading", line_start, line_end)
                continue

            if stripped.startswith(">") and (
                "[!" in stripped.upper() or stripped.startswith("> [!")
            ):
                self.text.tag_add("callout", line_start, line_end)
                continue

            for m in _BOLD_RE.finditer(line):
                self.text.tag_add(
                    "bold_span", f"{idx}.{m.start()}", f"{idx}.{m.end()}"
                )
            for m in _INLINE_CODE_RE.finditer(line):
                self.text.tag_add(
                    "inline_code", f"{idx}.{m.start()}", f"{idx}.{m.end()}"
                )

    def get_text(self) -> str:
        """Return the complete Markdown text in the editor."""
        return self.text.get("1.0", "end-1c")

    def set_text(self, content: str, trigger_callback: bool = False) -> None:
        """Replace editor text and refresh syntax tags, line numbers, and metrics."""
        self._suppress_change_event = not trigger_callback
        try:
            self.text.delete("1.0", tk.END)
            self.text.insert("1.0", content)
            self.text.edit_reset()
            self.text.edit_modified(False)
            self.apply_syntax_highlighting()
            self.update_metrics()
            self.redraw_line_numbers()
        finally:
            self._suppress_change_event = False

        if trigger_callback and self._on_debounced_change is not None:
            self._on_debounced_change(self.get_text())

    def scroll_to_line(self, line_number: int) -> None:
        """Scroll the editor to line_number and briefly highlight the line."""
        target_index = f"{max(1, line_number)}.0"
        self.text.see(target_index)
        self.text.mark_set(tk.INSERT, target_index)
        self.text.tag_remove("outline_flash", "1.0", tk.END)
        self.text.tag_add("outline_flash", target_index, f"{max(1, line_number)}.end")
        self.redraw_line_numbers()
        self.update_metrics()
        self.after(
            900, lambda: self.text.tag_remove("outline_flash", "1.0", tk.END)
        )

    # Snippet Insertion Helpers
    def insert_yaml_frontmatter_template(self) -> None:
        """Prepend or update a standard YAML frontmatter block at the top of the document."""
        current = self.get_text()
        if current.lstrip().startswith("---"):
            self.scroll_to_line(1)
            return
        template = (
            "---\n"
            "title: Technical Architecture Specification\n"
            "subtitle: Design, Implementation & Operational Verification\n"
            "author: Engineering Team\n"
            "date: 2026-11-12\n"
            "version: 1.0.0\n"
            "institution: Systems Publishing Studio\n"
            "cover: true\n"
            "toc: true\n"
            "header: TECHNICAL SPECIFICATION\n"
            "footer: Confidential - Internal Use Only\n"
            "---\n\n"
        )
        self.text.insert("1.0", template)
        self.scroll_to_line(1)

    def insert_bold_snippet(self) -> None:
        """Wrap current selection in **bold** or insert a bold placeholder at the cursor."""
        try:
            sel_start = self.text.index(tk.SEL_FIRST)
            sel_end = self.text.index(tk.SEL_LAST)
            selected = self.text.get(sel_start, sel_end)
            self.text.delete(sel_start, sel_end)
            self.text.insert(sel_start, f"**{selected}**")
        except tk.TclError:
            self.text.insert(tk.INSERT, "**bold text**")
        self.text.focus_set()

    def insert_code_block_snippet(self) -> None:
        """Insert a fenced Python code block template at the cursor."""
        snippet = (
            "\n```python\n"
            "def compute_throughput(ops: int, elapsed_sec: float) -> float:\n"
            "    return round(ops / max(elapsed_sec, 1e-6), 2)\n"
            "```\n"
        )
        self.text.insert(tk.INSERT, snippet)
        self.text.focus_set()

    def insert_table_snippet(self) -> None:
        """Insert a structured 3-column Markdown table at the cursor."""
        snippet = (
            "\n| Component | Specification | Status |\n"
            "| :--- | :--- | :--- |\n"
            "| Layout Engine | PyMuPDF `fitz.Story` | Verified |\n"
            "| Code Highlighter | Pygments Inline Styles | Active |\n"
        )
        self.text.insert(tk.INSERT, snippet)
        self.text.focus_set()

    def insert_callout_snippet(self, kind: str = "NOTE") -> None:
        """Insert a GitHub/Obsidian-style admonition callout block at the cursor."""
        snippet = (
            f"\n> [!{kind.upper()}]\n"
            "> Key architectural consideration or operational guidance for print readers.\n"
        )
        self.text.insert(tk.INSERT, snippet)
        self.text.focus_set()
