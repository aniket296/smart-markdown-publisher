"""Left-hand collapsible notebook with interactive Outline Treeview and Document Setup controls."""

import tkinter as tk
from tkinter import ttk
from typing import Callable

from src.models.document_model import DocumentMetadata, HeadingNode
from src.models.print_profile import PrintProfile


class OutlineSidebarPane(ttk.Frame):
    """Left-hand studio sidebar containing Tab 1 (Outline H1-H4 tree) and Tab 2 (Document Setup)."""

    def __init__(
        self,
        parent: tk.Misc,
        on_heading_selected: Callable[[int], None] | None = None,
        on_setup_changed: Callable[[dict[str, bool]], None] | None = None,
    ) -> None:
        super().__init__(parent, style="Studio.TFrame", padding=(4, 4))
        self._on_heading_selected = on_heading_selected
        self._on_setup_changed = on_setup_changed
        self._item_line_map: dict[str, int] = {}
        self._suppress_setup_callback = False

        self.cover_var = tk.BooleanVar(value=True)
        self.toc_var = tk.BooleanVar(value=True)
        self.page_numbers_var = tk.BooleanVar(value=True)
        self.running_header_var = tk.BooleanVar(value=True)

        self._build_ui()

    def _build_ui(self) -> None:
        self.notebook = ttk.Notebook(self, style="Studio.TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Interactive Heading Outline
        self.outline_tab = ttk.Frame(self.notebook, style="Surface.TFrame", padding=4)
        self.notebook.add(self.outline_tab, text="Outline")

        tree_container = ttk.Frame(self.outline_tab, style="Surface.TFrame")
        tree_container.pack(fill=tk.BOTH, expand=True)

        self.tree_scroll = ttk.Scrollbar(tree_container, orient=tk.VERTICAL)
        self.tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(
            tree_container,
            show="tree",
            selectmode="browse",
            style="Outline.Treeview",
            yscrollcommand=self.tree_scroll.set,
        )
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree_scroll.configure(command=self.tree.yview)

        self.tree.bind("<<TreeviewSelect>>", self._handle_tree_select)

        # Tab 2: Document Setup Checkboxes
        self.setup_tab = ttk.Frame(self.notebook, style="Surface.TFrame", padding=12)
        self.notebook.add(self.setup_tab, text="Document Setup")

        ttk.Label(
            self.setup_tab,
            text="FRONTMATTER & LAYOUT OPTIONS",
            style="SectionHeader.TLabel",
        ).pack(anchor=tk.W, pady=(0, 10))

        self._add_setup_checkbox(
            self.setup_tab,
            "Generate Cover Page",
            self.cover_var,
        )
        self._add_setup_checkbox(
            self.setup_tab,
            "Include Table of Contents",
            self.toc_var,
        )
        self._add_setup_checkbox(
            self.setup_tab,
            "Show Page X of Y Footers",
            self.page_numbers_var,
        )
        self._add_setup_checkbox(
            self.setup_tab,
            "Show Running Header",
            self.running_header_var,
        )

    def _add_setup_checkbox(
        self,
        parent: ttk.Frame,
        text: str,
        variable: tk.BooleanVar,
    ) -> ttk.Checkbutton:
        cb = ttk.Checkbutton(
            parent,
            text=text,
            variable=variable,
            command=self._handle_setup_toggle,
        )
        cb.pack(anchor=tk.W, pady=5)
        return cb

    def _handle_tree_select(self, _event: object = None) -> None:
        selection = self.tree.selection()
        if not selection:
            return
        item_id = selection[0]
        line_num = self._item_line_map.get(item_id)
        if line_num is not None and self._on_heading_selected is not None:
            self._on_heading_selected(line_num)

    def _handle_setup_toggle(self) -> None:
        if self._suppress_setup_callback or self._on_setup_changed is None:
            return
        self._on_setup_changed(self.get_setup_flags())

    def get_setup_flags(self) -> dict[str, bool]:
        """Return the current state of the 4 Document Setup checkboxes."""
        return {
            "include_cover": bool(self.cover_var.get()),
            "include_toc": bool(self.toc_var.get()),
            "show_page_numbers": bool(self.page_numbers_var.get()),
            "show_running_header": bool(self.running_header_var.get()),
        }

    def sync_from_metadata_and_profile(
        self,
        metadata: DocumentMetadata,
        profile: PrintProfile,
    ) -> None:
        """Synchronize Document Setup checkboxes with parsed YAML frontmatter and PrintProfile."""
        self._suppress_setup_callback = True
        try:
            self.cover_var.set(metadata.include_cover)
            self.toc_var.set(metadata.include_toc)
            self.page_numbers_var.set(profile.show_page_numbers)
            self.running_header_var.set(profile.show_running_header)
        finally:
            self._suppress_setup_callback = False

    def update_outline(self, headings: list[HeadingNode]) -> None:
        """Populate the interactive Treeview with the H1-H4 heading hierarchy."""
        for child in self.tree.get_children():
            self.tree.delete(child)
        self._item_line_map.clear()

        parent_stack: list[tuple[int, str]] = []
        for idx, h in enumerate(headings):
            if h.level > 4:
                continue

            while parent_stack and parent_stack[-1][0] >= h.level:
                parent_stack.pop()

            parent_id = parent_stack[-1][1] if parent_stack else ""
            prefix = f"H{h.level}  "
            item_id = f"heading_{idx}_L{h.line_number}"
            self.tree.insert(
                parent_id,
                tk.END,
                iid=item_id,
                text=f"{prefix}{h.text}",
                open=True,
            )
            self._item_line_map[item_id] = h.line_number
            parent_stack.append((h.level, item_id))
