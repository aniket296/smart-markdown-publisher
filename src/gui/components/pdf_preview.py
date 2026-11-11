"""Right-hand live paginated PDF preview pane with navigation, zoom, and compile timing."""

import tkinter as tk
from tkinter import ttk
from typing import Callable
from PIL import Image, ImageTk

from src.gui.styles import FONT_SMALL, FONT_UI_BOLD, SLATE_CANVAS, SLATE_SIDEBAR


class PdfPreviewPane(ttk.Frame):
    """Live paginated PDF preview pane displaying crisp drop-shadowed pages on a dark-slate canvas."""

    ZOOM_PRESETS = {
        "75%": 390,
        "100%": 520,
        "125%": 650,
    }

    def __init__(
        self,
        parent: tk.Misc,
        on_page_or_zoom_changed: Callable[[int, int], None] | None = None,
    ) -> None:
        super().__init__(parent, style="Studio.TFrame")
        self._on_page_or_zoom_changed = on_page_or_zoom_changed
        self._current_page_index = 0
        self._total_pages = 1
        self._photo_image: ImageTk.PhotoImage | None = None

        self.page_badge_var = tk.StringVar(value="Page 1 of 1")
        self.zoom_var = tk.StringVar(value="100%")
        self.compile_time_var = tk.StringVar(value="Ready")

        self._build_ui()

    def _build_ui(self) -> None:
        # Top Navigation & Zoom Bar
        nav_bar = ttk.Frame(self, style="Studio.TFrame", padding=(8, 4))
        nav_bar.pack(side=tk.TOP, fill=tk.X)

        self.first_btn = ttk.Button(
            nav_bar,
            text="|< First",
            style="Secondary.TButton",
            command=self.go_first_page,
        )
        self.first_btn.pack(side=tk.LEFT, padx=2)

        self.prev_btn = ttk.Button(
            nav_bar,
            text="< Prev Page",
            style="Secondary.TButton",
            command=self.go_prev_page,
        )
        self.prev_btn.pack(side=tk.LEFT, padx=2)

        self.page_badge = tk.Label(
            nav_bar,
            textvariable=self.page_badge_var,
            bg="#0F172A",
            fg="#F8FAFC",
            font=FONT_UI_BOLD,
            padx=10,
            pady=3,
        )
        self.page_badge.pack(side=tk.LEFT, padx=6)

        self.next_btn = ttk.Button(
            nav_bar,
            text="Next Page >",
            style="Secondary.TButton",
            command=self.go_next_page,
        )
        self.next_btn.pack(side=tk.LEFT, padx=2)

        self.last_btn = ttk.Button(
            nav_bar,
            text="Last >|",
            style="Secondary.TButton",
            command=self.go_last_page,
        )
        self.last_btn.pack(side=tk.LEFT, padx=2)

        # Zoom Selector on Right
        self.zoom_combo = ttk.Combobox(
            nav_bar,
            textvariable=self.zoom_var,
            values=list(self.ZOOM_PRESETS.keys()),
            state="readonly",
            width=6,
            style="Toolbar.TCombobox",
        )
        self.zoom_combo.pack(side=tk.RIGHT, padx=(4, 0))
        self.zoom_combo.bind("<<ComboboxSelected>>", self._on_zoom_selected)

        ttk.Label(nav_bar, text="Zoom:", style="SectionHeader.TLabel").pack(
            side=tk.RIGHT, padx=(8, 2)
        )

        # Scrollable Dark-Slate Backdrop Canvas (#334155)
        canvas_container = ttk.Frame(self, style="Studio.TFrame")
        canvas_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.v_scroll = ttk.Scrollbar(canvas_container, orient=tk.VERTICAL)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.h_scroll = ttk.Scrollbar(canvas_container, orient=tk.HORIZONTAL)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas = tk.Canvas(
            canvas_container,
            bg=SLATE_CANVAS,
            highlightthickness=0,
            bd=0,
            yscrollcommand=self.v_scroll.set,
            xscrollcommand=self.h_scroll.set,
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.v_scroll.configure(command=self.canvas.yview)
        self.h_scroll.configure(command=self.canvas.xview)

        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind("<MouseWheel>", self._on_canvas_mousewheel)

        # Bottom Status Bar with Compile Time Indicator
        status_frame = tk.Frame(self, bg=SLATE_SIDEBAR, padx=10, pady=4)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.compile_label = tk.Label(
            status_frame,
            textvariable=self.compile_time_var,
            bg=SLATE_SIDEBAR,
            fg="#99F6E4",
            font=FONT_SMALL,
            anchor=tk.E,
        )
        self.compile_label.pack(side=tk.RIGHT)

    def _on_canvas_mousewheel(self, event: tk.Event) -> None:
        delta = int(-1 * (event.delta / 120))
        self.canvas.yview_scroll(delta, "units")

    def _on_canvas_configure(self, _event: tk.Event) -> None:
        self._recenter_canvas_items()

    def _on_zoom_selected(self, _event: object = None) -> None:
        self._notify_page_or_zoom()

    def get_target_width(self) -> int:
        """Return target pixel width for the active zoom level."""
        return self.ZOOM_PRESETS.get(self.zoom_var.get(), 520)

    def get_current_page_index(self) -> int:
        """Return 0-based active page index."""
        return self._current_page_index

    def go_first_page(self) -> None:
        if self._current_page_index != 0:
            self._current_page_index = 0
            self._notify_page_or_zoom()

    def go_prev_page(self) -> None:
        if self._current_page_index > 0:
            self._current_page_index -= 1
            self._notify_page_or_zoom()

    def go_next_page(self) -> None:
        if self._current_page_index < self._total_pages - 1:
            self._current_page_index += 1
            self._notify_page_or_zoom()

    def go_last_page(self) -> None:
        last_idx = max(0, self._total_pages - 1)
        if self._current_page_index != last_idx:
            self._current_page_index = last_idx
            self._notify_page_or_zoom()

    def _notify_page_or_zoom(self) -> None:
        if self._on_page_or_zoom_changed is not None:
            self._on_page_or_zoom_changed(
                self._current_page_index, self.get_target_width()
            )

    def display_rendered_page(
        self,
        pil_image: Image.Image,
        page_index: int,
        total_pages: int,
        compile_ms: float | None = None,
    ) -> None:
        """Display the rendered PIL image on the dark-slate canvas with a drop shadow."""
        self._total_pages = max(1, total_pages)
        self._current_page_index = max(0, min(page_index, self._total_pages - 1))

        self.page_badge_var.set(
            f"Page {self._current_page_index + 1} of {self._total_pages}"
        )
        if compile_ms is not None:
            self.compile_time_var.set(f"Typeset in {int(round(compile_ms))} ms")

        self._photo_image = ImageTk.PhotoImage(pil_image)
        self._draw_page_on_canvas(pil_image.width, pil_image.height)

    def _draw_page_on_canvas(self, img_w: int, img_h: int) -> None:
        self.canvas.delete("all")
        if self._photo_image is None:
            return

        canvas_w = max(self.canvas.winfo_width(), img_w + 48)
        pad_y = 24
        x_center = canvas_w // 2
        left = x_center - (img_w // 2)
        top = pad_y

        # Drop shadow rectangle behind the page
        self.canvas.create_rectangle(
            left + 6,
            top + 6,
            left + img_w + 6,
            top + img_h + 6,
            fill="#0F172A",
            outline="",
            tags="shadow",
        )
        self.canvas.create_image(
            left,
            top,
            anchor=tk.NW,
            image=self._photo_image,
            tags="page_img",
        )
        self.canvas.configure(
            scrollregion=(0, 0, canvas_w, img_h + pad_y * 2 + 12)
        )

    def _recenter_canvas_items(self) -> None:
        if self._photo_image is None:
            return
        self._draw_page_on_canvas(
            self._photo_image.width(), self._photo_image.height()
        )
