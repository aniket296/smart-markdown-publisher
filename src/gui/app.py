"""Main Desktop Publishing Studio Shell with 3-pane workspace and background PDF typesetting."""

import ctypes
from pathlib import Path
import queue
import re
import sys
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image

from src.core.book_binder import bind_folder_manuscript
from src.core.md_compiler import compile_markdown
from src.core.pdf_typesetter import render_pdf_page_preview, typeset_to_pdf_bytes
from src.gui.components.markdown_editor import MarkdownEditorPane
from src.gui.components.outline_sidebar import OutlineSidebarPane
from src.gui.components.pdf_preview import PdfPreviewPane
from src.gui.components.toolbar import PublishingToolbar
from src.gui.styles import WORKSPACE_BG, apply_studio_theme
from src.models.document_model import CompiledManuscript
from src.models.print_profile import PrintProfile
from src.utils.config import (
    get_default_page_size,
    get_default_theme,
    get_preview_debounce_ms,
)
from src.utils.logger import get_logger

logger = get_logger("gui.app")

SHOWCASE_STARTER_DOCUMENT = """---
title: Smart Markdown-to-Print Publishing Architecture
subtitle: Offline Technical Typesetting with PyMuPDF Story, Pygments & Print Profiles
author: Principal Systems Engineering Studio
date: 2026-11-12
version: 1.0.0
institution: Technical Publishing Division
cover: true
toc: true
header: ARCHITECTURE & TYPESETTING SPECIFICATION
footer: Smart Markdown-to-Print Desktop Publisher - Offline Studio
---

# 1. Architectural Overview

**Smart Markdown-to-Print Desktop Publisher** transforms standard Markdown (`.md`) manuscripts into publication-ready, vector-typeset PDF documents completely offline—eliminating multi-gigabyte LaTeX distributions or external cloud dependencies.

The core typesetting pipeline integrates four deterministic stages:

1. **YAML Frontmatter Extraction:** Parses document metadata (`title`, `subtitle`, `author`, `institution`, `cover`, `toc`) and configures cover page and running header/footer parameters.
2. **Admonition Callout Preprocessor:** Transforms GitHub and Obsidian blockquotes (`> [!NOTE]`, `> [!WARNING]`, `> [!TIP]`) into styled print callout boxes.
3. **Offline Pygments Code Formatter:** Highlights source code blocks with inline styles and automatic line wrapping so code never overflows page margins.
4. **PyMuPDF `fitz.Story` Layout Engine:** Paginates HTML + print CSS across `A4` or `Letter` pages, stamps two-pass `Page X of Y` footers, and embeds clickable PDF bookmark trees.

> [!NOTE]
> Try switching between **Academic**, **Technical**, **Executive**, and **Compact** themes in the top toolbar to see real-time typography and layout updates in the PDF preview pane!

## 1.1 Deterministic Pagination Algorithm

Below is the core pagination loop used to place typeset story frames across pages while reserving vertical margins for running headers and footers:

```python
import fitz

def paginate_story_frames(story: fitz.Story, mediabox: fitz.Rect, margin: float) -> bytes:
    buffer = fitz.io.BytesIO()
    writer = fitz.DocumentWriter(buffer)
    inner_rect = fitz.Rect(margin, margin + 10, mediabox.width - margin, mediabox.height - margin - 12)

    more = 1
    while more:
        device = writer.begin_page(mediabox)
        more, _ = story.place(inner_rect)
        story.draw(device)
        writer.end_page()

    writer.close()
    return buffer.getvalue()
```

> [!TIP] Multi-Chapter Book Binding
> Use **Bind Folder as Book...** in the toolbar to combine an entire directory of numbered chapter files (`01_intro.md`, `02_design.md`, `03_appendix.md`) into a unified book with automatic chapter page breaks.

# 2. Print Theme & Typography Benchmarks

Each built-in print profile is tuned for specific technical and scholarly publishing workflows:

| Theme Profile | Primary Typography | Target Publishing Use Case | Avg. Compile Time |
| :--- | :--- | :--- | :---: |
| **Technical** | Clean Sans-Serif + Slate Grid | API Specs, RFCs & System Architecture Docs | 28 ms |
| **Academic** | Justified Serif + Classic Rules | Research Papers, Theses & Lab Manuscripts | 31 ms |
| **Executive** | High-Contrast Navy + Wide Leading | Whitepapers, Board Briefings & Proposals | 29 ms |
| **Compact** | Dense Scaling + Tight Spacing | Reference Sheets, Syllabi & Exam Handouts | 25 ms |

## 2.1 Operational Safety & Verification

> [!WARNING] Offline Asset Resolution
> Relative image links such as `![diagram](./assets/flow.png)` are resolved automatically against the active Markdown file's parent directory so embedded figures render reliably in offline environments.

### 2.1.1 Pre-Publication Checklist

- Verify document `title`, `author`, and `version` in the YAML frontmatter block.
- Inspect the **Outline** tab on the left to jump directly to any `H1`–`H4` section.
- Click **Export Typeset PDF** in the top-right corner to save the final PDF.
"""


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


def _update_yaml_boolean_flag(raw_text: str, key: str, enabled: bool) -> str:
    """Update or insert a boolean flag (`cover` or `toc`) inside the YAML frontmatter block."""
    val_str = "true" if enabled else "false"
    stripped = raw_text.lstrip("\ufeff")
    if stripped.startswith("---"):
        end_idx = stripped.find("\n---", 3)
        if end_idx != -1:
            yaml_part = stripped[3:end_idx]
            rest = stripped[end_idx:]
            pattern = re.compile(rf"^([ \t]*{re.escape(key)}[ \t]*:[ \t]*).*$", re.MULTILINE)
            if pattern.search(yaml_part):
                yaml_part = pattern.sub(rf"\g<1>{val_str}", yaml_part)
            else:
                yaml_part = yaml_part.rstrip() + f"\n{key}: {val_str}\n"
            return f"---{yaml_part}{rest}"

    return f"---\n{key}: {val_str}\n---\n\n{raw_text}"


class SmartMarkdownPublisherApp:
    """Primary Tkinter/TTK desktop application controller."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Smart Markdown-to-Print Desktop Publisher")
        self.root.geometry("1440x880")
        self.root.minsize(1060, 680)
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
        self.current_file_path: Path | None = None
        self.latest_pdf_bytes: bytes = b""
        self.latest_manuscript: CompiledManuscript | None = None
        self._render_generation = 0
        self._render_lock = threading.Lock()
        self._result_queue: queue.Queue[
            tuple[int, CompiledManuscript, bytes, Image.Image, int, int, float]
        ] = queue.Queue()

        self._build_layout()
        self.root.after(25, self._poll_typeset_results)
        self.load_showcase_document()

    def _build_layout(self) -> None:
        # Top Publishing Toolbar
        self.toolbar = PublishingToolbar(
            self.root,
            initial_profile=self.profile,
            on_action=self._on_toolbar_action,
            on_profile_change=self._on_profile_changed,
        )
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # 3-Pane Studio Workspace (Left: Outline/Setup, Center: Markdown Editor, Right: Live PDF Preview)
        self.paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=6, pady=6)

        self.sidebar = OutlineSidebarPane(
            self.paned,
            on_heading_selected=self._on_outline_heading_clicked,
            on_setup_changed=self._on_setup_drawer_changed,
        )
        self.editor = MarkdownEditorPane(
            self.paned,
            debounce_ms=get_preview_debounce_ms(),
            on_debounced_change=self._on_editor_text_changed,
        )
        self.preview = PdfPreviewPane(
            self.paned,
            on_page_or_zoom_changed=self._on_preview_page_or_zoom_changed,
        )

        self.paned.add(self.sidebar, weight=1)
        self.paned.add(self.editor, weight=3)
        self.paned.add(self.preview, weight=3)

    def load_showcase_document(self) -> None:
        """Load the built-in Showcase Starter Document and trigger initial background typesetting."""
        self.current_file_path = None
        self.root.title("Smart Markdown-to-Print Desktop Publisher — Showcase Manuscript")
        self.editor.set_text(SHOWCASE_STARTER_DOCUMENT, trigger_callback=True)

    def _on_toolbar_action(self, action_id: str) -> None:
        logger.info("Toolbar action triggered: %s", action_id)
        if action_id == "new_sample":
            self.load_showcase_document()
        elif action_id == "open_md":
            self.action_open_markdown()
        elif action_id == "save_md":
            self.action_save_markdown()
        elif action_id == "bind_folder":
            self.action_bind_folder_book()
        elif action_id == "export_pdf":
            self.action_export_pdf()
        elif action_id == "insert_yaml":
            self.editor.insert_yaml_frontmatter_template()
            self._schedule_background_typeset(self.editor.get_text())
        elif action_id == "insert_bold":
            self.editor.insert_bold_snippet()
            self._schedule_background_typeset(self.editor.get_text())
        elif action_id == "insert_code":
            self.editor.insert_code_block_snippet()
            self._schedule_background_typeset(self.editor.get_text())
        elif action_id == "insert_table":
            self.editor.insert_table_snippet()
            self._schedule_background_typeset(self.editor.get_text())
        elif action_id == "insert_callout":
            self.editor.insert_callout_snippet("NOTE")
            self._schedule_background_typeset(self.editor.get_text())

    def _on_profile_changed(self, profile: PrintProfile) -> None:
        self.profile = profile
        self._schedule_background_typeset(self.editor.get_text())

    def _on_outline_heading_clicked(self, line_number: int) -> None:
        self.editor.scroll_to_line(line_number)

    def _on_setup_drawer_changed(self, flags: dict[str, bool]) -> None:
        self.profile.show_page_numbers = flags.get("show_page_numbers", True)
        self.profile.show_running_header = flags.get("show_running_header", True)

        raw_md = self.editor.get_text()
        updated_md = _update_yaml_boolean_flag(
            raw_md, "cover", flags.get("include_cover", False)
        )
        updated_md = _update_yaml_boolean_flag(
            updated_md, "toc", flags.get("include_toc", False)
        )
        if updated_md != raw_md:
            self.editor.set_text(updated_md, trigger_callback=False)

        self._schedule_background_typeset(self.editor.get_text())

    def _on_editor_text_changed(self, markdown_text: str) -> None:
        self._schedule_background_typeset(markdown_text)

    def _on_preview_page_or_zoom_changed(self, page_index: int, target_width: int) -> None:
        if not self.latest_pdf_bytes:
            return
        try:
            pil_img, total_pages = render_pdf_page_preview(
                self.latest_pdf_bytes,
                page_index=page_index,
                max_width=target_width,
            )
            self.preview.display_rendered_page(pil_img, page_index, total_pages)
        except Exception as exc:
            logger.error("Failed to re-render preview page: %s", exc)

    def _schedule_background_typeset(self, markdown_text: str) -> None:
        with self._render_lock:
            self._render_generation += 1
            gen_id = self._render_generation

        base_dir = (
            str(self.current_file_path.parent)
            if self.current_file_path is not None
            else str(Path.cwd())
        )
        profile_snapshot = PrintProfile(
            page_size=self.profile.page_size,
            theme=self.profile.theme,
            margins=self.profile.margins,
            show_page_numbers=self.profile.show_page_numbers,
            show_running_header=self.profile.show_running_header,
            base_font_size=self.profile.base_font_size,
        )
        active_page_idx = self.preview.get_current_page_index()
        target_width = self.preview.get_target_width()

        worker = threading.Thread(
            target=self._background_typeset_worker,
            args=(
                gen_id,
                markdown_text,
                base_dir,
                profile_snapshot,
                active_page_idx,
                target_width,
            ),
            daemon=True,
        )
        worker.start()

    def _background_typeset_worker(
        self,
        gen_id: int,
        markdown_text: str,
        base_dir: str,
        profile_snapshot: PrintProfile,
        page_idx: int,
        target_width: int,
    ) -> None:
        t0 = time.perf_counter()
        try:
            manuscript = compile_markdown(markdown_text, base_dir=base_dir)
            pdf_bytes = typeset_to_pdf_bytes(
                manuscript,
                profile=profile_snapshot,
                asset_dir=base_dir,
            )
            pil_img, total_pages = render_pdf_page_preview(
                pdf_bytes,
                page_index=page_idx,
                max_width=target_width,
            )
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
        except Exception as exc:
            logger.error("Background PDF typesetting error: %s", exc)
            return

        with self._render_lock:
            if gen_id != self._render_generation:
                return

        self._result_queue.put(
            (
                gen_id,
                manuscript,
                pdf_bytes,
                pil_img,
                page_idx,
                total_pages,
                elapsed_ms,
            )
        )

    def _poll_typeset_results(self) -> None:
        """Drain completed background typesetting results on the Tkinter main thread via root.after()."""
        latest_item = None
        while True:
            try:
                latest_item = self._result_queue.get_nowait()
            except queue.Empty:
                break

        if latest_item is not None:
            self._apply_typeset_result_on_main_thread(*latest_item)

        try:
            self.root.after(25, self._poll_typeset_results)
        except tk.TclError:
            pass

    def _apply_typeset_result_on_main_thread(
        self,
        gen_id: int,
        manuscript: CompiledManuscript,
        pdf_bytes: bytes,
        pil_img: Image.Image,
        page_idx: int,
        total_pages: int,
        elapsed_ms: float,
    ) -> None:
        if gen_id != self._render_generation:
            return
        self.latest_manuscript = manuscript
        self.latest_pdf_bytes = pdf_bytes
        self.sidebar.update_outline(manuscript.headings)
        self.sidebar.sync_from_metadata_and_profile(manuscript.metadata, self.profile)
        self.preview.display_rendered_page(
            pil_img,
            page_index=page_idx,
            total_pages=total_pages,
            compile_ms=elapsed_ms,
        )

    # File Dialog Workflows
    def action_open_markdown(self) -> None:
        """Open a Markdown (.md) file from disk into the studio editor."""
        path_str = filedialog.askopenfilename(
            parent=self.root,
            title="Open Markdown Manuscript",
            filetypes=[
                ("Markdown Files", "*.md *.markdown *.txt"),
                ("All Files", "*.*"),
            ],
        )
        if not path_str:
            return
        try:
            file_path = Path(path_str).resolve()
            content = file_path.read_text(encoding="utf-8")
            self.current_file_path = file_path
            self.root.title(
                f"Smart Markdown-to-Print Desktop Publisher — {file_path.name}"
            )
            self.editor.set_text(content, trigger_callback=True)
            logger.info("Opened Markdown file: %s", file_path)
        except Exception as exc:
            logger.error("Failed to open Markdown file: %s", exc)
            messagebox.showerror(
                "Open File Error",
                f"Could not open Markdown file:\n{exc}",
                parent=self.root,
            )

    def action_save_markdown(self) -> None:
        """Save the active Markdown manuscript to disk."""
        initial_name = (
            self.current_file_path.name
            if self.current_file_path is not None
            else "manuscript.md"
        )
        path_str = filedialog.asksaveasfilename(
            parent=self.root,
            title="Save Markdown Manuscript",
            defaultextension=".md",
            initialfile=initial_name,
            filetypes=[
                ("Markdown Files", "*.md"),
                ("All Files", "*.*"),
            ],
        )
        if not path_str:
            return
        try:
            file_path = Path(path_str).resolve()
            file_path.write_text(self.editor.get_text(), encoding="utf-8")
            self.current_file_path = file_path
            self.root.title(
                f"Smart Markdown-to-Print Desktop Publisher — {file_path.name}"
            )
            logger.info("Saved Markdown file: %s", file_path)
        except Exception as exc:
            logger.error("Failed to save Markdown file: %s", exc)
            messagebox.showerror(
                "Save File Error",
                f"Could not save Markdown file:\n{exc}",
                parent=self.root,
            )

    def action_bind_folder_book(self) -> None:
        """Bind a folder of ordered .md chapters into a multi-chapter manuscript."""
        folder_str = filedialog.askdirectory(
            parent=self.root,
            title="Select Folder Containing Ordered Markdown Chapters (.md)",
        )
        if not folder_str:
            return
        try:
            bound_markdown = bind_folder_manuscript(folder_str)
            folder_path = Path(folder_str).resolve()
            self.current_file_path = folder_path / "bound_book.md"
            self.root.title(
                f"Smart Markdown-to-Print Desktop Publisher — Book: {folder_path.name}"
            )
            self.editor.set_text(bound_markdown, trigger_callback=True)
            logger.info("Bound folder as book: %s", folder_path)
        except Exception as exc:
            logger.error("Failed to bind folder as book: %s", exc)
            messagebox.showerror(
                "Book Binder Error",
                f"Could not bind folder into book manuscript:\n{exc}",
                parent=self.root,
            )

    def action_export_pdf(self) -> None:
        """Compile and save the publication-ready typeset PDF to disk."""
        default_stem = "typeset_manuscript"
        if self.current_file_path is not None:
            default_stem = self.current_file_path.stem
        elif self.latest_manuscript and self.latest_manuscript.metadata.title:
            slug = re.sub(
                r"[^a-zA-Z0-9_-]+",
                "_",
                self.latest_manuscript.metadata.title.strip().lower(),
            ).strip("_")
            if slug:
                default_stem = slug

        path_str = filedialog.asksaveasfilename(
            parent=self.root,
            title="Export Typeset PDF",
            defaultextension=".pdf",
            initialfile=f"{default_stem}.pdf",
            filetypes=[("PDF Document", "*.pdf")],
        )
        if not path_str:
            return

        try:
            base_dir = (
                str(self.current_file_path.parent)
                if self.current_file_path is not None
                else str(Path.cwd())
            )
            manuscript = compile_markdown(self.editor.get_text(), base_dir=base_dir)
            pdf_bytes = typeset_to_pdf_bytes(
                manuscript,
                profile=self.profile,
                asset_dir=base_dir,
            )
            out_path = Path(path_str).resolve()
            out_path.write_bytes(pdf_bytes)
            logger.info("Exported typeset PDF to: %s (%d bytes)", out_path, len(pdf_bytes))
            messagebox.showinfo(
                "PDF Export Complete",
                f"Successfully exported typeset PDF:\n{out_path}",
                parent=self.root,
            )
        except Exception as exc:
            logger.error("Failed to export PDF: %s", exc)
            messagebox.showerror(
                "Export PDF Error",
                f"Could not export typeset PDF:\n{exc}",
                parent=self.root,
            )
