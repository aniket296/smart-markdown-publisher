<div align="center">

# Smart Markdown-to-Print Desktop Publisher

**Offline Desktop Writing & Typesetting Studio for Technical Writers, Educators, and Engineers**

[![Platform: Windows 10/11](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/YOUR_USERNAME/smart-markdown-publisher)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Architecture: Offline-First](https://img.shields.io/badge/Privacy-100%25%20Offline--First-0D9488?style=for-the-badge)](https://github.com/YOUR_USERNAME/smart-markdown-publisher)
[![Engine: PyMuPDF Story](https://img.shields.io/badge/Layout%20Engine-PyMuPDF%20fitz.Story-1E293B?style=for-the-badge)](https://pymupdf.readthedocs.io/)
[![Packaging: PyInstaller & Inno Setup](https://img.shields.io/badge/Packaging-PyInstaller%20%2B%20Inno%20Setup-F59E0B?style=for-the-badge)](https://pyinstaller.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](LICENSE)

</div>

---

## Why This Exists (Real-World Impact)

Engineers, researchers, and educators love writing in clean **Markdown (`.md`)**, but turning a technical manuscript into a **publication-ready, paginated PDF** often forces an unpleasant trade-off:

1. **Multi-Gigabyte LaTeX Distributions:** Installing TeX Live or MiKTeX requires gigabytes of packages, fragile font configurations, and cryptic compilation errors.
2. **Browser "Print-to-PDF" Artifacts:** Exporting from web viewers produces awkward page breaks, unnumbered pages, missing cover pages, and overflowing code blocks.
3. **Cloud Privacy Risks:** Uploading confidential engineering specifications, proprietary RFCs, or unpublished exams to third-party web converters violates enterprise security policies.

**Smart Markdown-to-Print Desktop Publisher** solves this completely offline in a single native Windows desktop studio. Powered by the **`PyMuPDF` (`fitz.Story`)** layout engine and **`Pygments`**, it compiles standard Markdown with YAML frontmatter into crisp, vector-typeset PDFs in ~30 milliseconds—complete with vector cover pages, Tables of Contents, syntax-highlighted code blocks, callout boxes, running headers, `Page X of Y` footers, and clickable PDF bookmark outlines.

---

## Key Features

- **YAML Frontmatter & Vector Cover Page Generation:** Define `title`, `subtitle`, `author`, `date`, `version`, `institution`, `cover: true`, and `toc: true` at the top of your Markdown file to automatically generate a dedicated vector cover page and structured Table of Contents.
- **4 Curated Print Typography Themes:**
  - **`Technical`:** Clean sans-serif typography, slate-tinted code containers, bold teal section rules, and high-contrast grid tables.
  - **`Academic`:** Classic serif typography (`Times` / `Georgia`), justified paragraphs, centered section headers, and scholarly table borders.
  - **`Executive`:** High-contrast navy headers, generous line-height, accent blockquotes, and modern whitepaper spacing.
  - **`Compact`:** Tight vertical spacing and condensed font scaling tailored for dense reference guides, syllabi, and exam handouts.
- **GitHub / Obsidian Admonition Callout Boxes:** Native support for `> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!WARNING]`, and `> [!CAUTION]` blockquotes—rendered into distinct, color-accented print callout containers.
- **Offline `Pygments` Syntax Highlighting:** Highlights fenced code blocks across 500+ languages with inline styles and intelligent line wrapping so code never overflows horizontally on PDF pages.
- **Two-Pass Running Headers & `Page X of Y` Footers:** Automatically stamps document titles, custom headers/footers, subtle hairline rules, and exact `Page X of Y` pagination across all content pages.
- **Clickable PDF Bookmark Outlines (`doc.set_toc()`):** Maps `H1`–`H6` headings to their exact rendered page numbers in the native PDF viewer bookmark tree.
- **Multi-Chapter Folder Book Binder:** Point **Bind Folder as Book...** at any directory of numbered Markdown files (`01_intro.md`, `02_architecture.md`, `10_appendix.md`) to merge them in natural sort order with automatic chapter page breaks.
- **3-Pane High-DPI Desktop Studio:** Features an interactive `H1`–`H4` outline tree, a line-numbered Markdown editor with live syntax highlighting and reading-time metrics, and a real-time paginated PDF preview canvas.

---

## Visual Architecture & Directory Tree

```text
smart-markdown-publisher/
├── .gitignore
├── .env.example
├── README.md
├── pyproject.toml
├── requirements.txt
├── run_local.bat                 # One-click local virtual environment setup & launcher
├── build_windows.spec            # PyInstaller standalone executable specification
├── assets/
│   └── app_icon.ico              # Multi-resolution (16, 32, 48, 256px) studio icon
├── installer/
│   └── setup.iss                 # Inno Setup 6 Windows installer script
├── scripts/
│   ├── generate_icon.py          # Programmatic Pillow icon badge generator
│   ├── build_exe.bat             # Automated pytest + PyInstaller EXE pipeline
│   └── build_installer.bat       # Full EXE + Inno Setup installer pipeline with fallback
├── src/
│   ├── __init__.py
│   ├── main.py                   # High-DPI awareness & studio entrypoint
│   ├── core/
│   │   ├── __init__.py
│   │   ├── frontmatter_parser.py # YAML frontmatter parser with H1 title fallback
│   │   ├── callout_processor.py  # GitHub/Obsidian [!NOTE] & [!WARNING] preprocessor
│   │   ├── md_compiler.py        # Markdown + Pygments compiler & heading extractor
│   │   ├── theme_registry.py     # Print CSS generator for 4 typography themes
│   │   ├── book_binder.py        # Natural-sorted multi-chapter folder binder
│   │   └── pdf_typesetter.py     # PyMuPDF fitz.Story pagination, cover & footers
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── app.py                # 3-pane studio controller & background worker thread
│   │   ├── styles.py             # Slate-Teal TTK "clam" desktop publishing theme
│   │   └── components/
│   │       ├── __init__.py
│   │       ├── toolbar.py        # File, snippet insertion & print profile toolbar
│   │       ├── outline_sidebar.py# H1-H4 outline tree & Document Setup drawer
│   │       ├── markdown_editor.py# Line-numbered editor & live word/reading metrics
│   │       └── pdf_preview.py    # Paginated PDF preview canvas with zoom & timing
│   ├── models/
│   │   ├── __init__.py
│   │   ├── document_model.py     # DocumentMetadata, HeadingNode, CompiledManuscript
│   │   └── print_profile.py      # PageSize, ThemeId, MarginPreset, PrintProfile
│   └── utils/
│       ├── __init__.py
│       ├── config.py             # Typed .env configuration loader
│       ├── path_resolver.py      # Relative Markdown/HTML image path resolver
│       └── logger.py             # Rotating file logger & thread-safe UI queue
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_parser_and_callouts.py
    ├── test_compiler_and_themes.py
    └── test_pdf_typesetter.py
```

```
+-----------------------------------------------------------------------------------+
|                        Smart Markdown-to-Print Studio (GUI)                       |
|  [PublishingToolbar]   [OutlineSidebarPane]   [MarkdownEditorPane]   [PdfPreview] |
+-----------------------------------------+-----------------------------------------+
                                          | Debounced Background Worker (350ms)
                                          v
+-----------------------------------------------------------------------------------+
|                          Core Compilation Pipeline (src/core)                     |
|  parse_frontmatter() -> resolve_markdown_image_paths() -> Pygments Highlighting   |
|                      -> preprocess_callouts()          -> Python-Markdown HTML    |
+-----------------------------------------+-----------------------------------------+
                                          | CompiledManuscript + PrintProfile
                                          v
+-----------------------------------------------------------------------------------+
|                        PyMuPDF Typesetting Engine (pdf_typesetter)                |
|  1. Vector Cover Page  2. fitz.Story Pagination  3. Running Headers & Footers     |
|  4. Native PDF Bookmark Tree (doc.set_toc)       5. Preview Rasterization (PIL)   |
+-----------------------------------------------------------------------------------+
```

---

## Quickstart Guide (4 Options)

### Option 1: Windows Installer (`SmartMarkdownPublisher_Setup.exe` from GitHub Releases)

1. Download **`SmartMarkdownPublisher_Setup.exe`** from the **Releases** page.
2. Run the installer to configure Start Menu / Desktop shortcuts and launch **Smart Markdown-to-Print Desktop Publisher** immediately—no Python installation required.

### Option 2: One-Click Local Source Launcher (`run_local.bat`)

Double-click **`run_local.bat`** (or run it from Command Prompt / PowerShell):

```bat
run_local.bat
```

It automatically creates `.venv` if missing, installs `requirements.txt`, generates `assets\app_icon.ico`, and launches the desktop studio.

### Option 3: Developer Terminal Setup (`venv` + `pip install -e .`)

```powershell
# 1. Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install package in editable mode with dev dependencies
pip install -e ".[dev]"

# 3. Generate application icon and launch studio
python scripts/generate_icon.py
python -m src.main
```

### Option 4: Rebuilding the Standalone `.exe` & Installer

```bat
:: Build standalone executable (dist\SmartMarkdownPublisher.exe)
scripts\build_exe.bat

:: Build standalone executable + Inno Setup installer (dist_installer\SmartMarkdownPublisher_Setup.exe)
scripts\build_installer.bat
```

> **Note:** `scripts\build_installer.bat` automatically detects Inno Setup 6 (`ISCC.exe`). If Inno Setup is not installed, it exits cleanly with code `0` after confirming that `dist\SmartMarkdownPublisher.exe` is ready to run.

---

## Markdown & Frontmatter Cheat Sheet

Place a YAML frontmatter block at the very top of your `.md` manuscript to control cover page generation, Table of Contents, and running headers/footers:

````markdown
---
title: Distributed Storage Engine Architecture
subtitle: Consensus, Write-Ahead Logging & B-Tree Compaction
author: Dr. Evelyn Vance
date: 2026-11-12
version: 2.4.0
institution: Systems Research Lab
cover: true
toc: true
header: CONFIDENTIAL TECHNICAL SPEC
footer: Systems Research Lab - Internal Distribution
---

# 1. Executive Summary

Write standard Markdown paragraphs with **bold**, *italic*, and `inline code`.

> [!NOTE]
> Use `> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!WARNING]`, or `> [!CAUTION]`
> to render styled admonition callout boxes in your PDF.

> [!WARNING] Production Checklist
> You can also provide a custom title right after the callout tag!

```python
def verify_quorum(nodes: int) -> int:
    return (nodes // 2) + 1
```

| Metric | Target | Verified |
| :--- | :---: | :---: |
| Write Latency (P99) | < 5.0 ms | 3.8 ms |
| Replication Factor | 3x | 3x |
````

---

## Tech Stack & Automated Testing

| Layer | Technology | Role |
| :--- | :--- | :--- |
| **PDF Layout Engine** | `PyMuPDF` (`fitz.Story`) `>=1.24.0` | HTML/CSS story pagination, vector cover drawing, running footers & TOC bookmarks |
| **Syntax Highlighting** | `Pygments` `>=2.17.2` | Offline inline syntax highlighting across 500+ programming languages |
| **Markdown & YAML** | `Markdown` `>=3.6` & `PyYAML` `>=6.0.1` | Frontmatter extraction, tables, fenced code, and heading tree parsing |
| **Desktop GUI** | `Tkinter` / `ttk` + `Pillow` `>=10.0.0` | High-DPI Windows studio shell, Slate-Teal theme, and live page rasterization |
| **Packaging** | `PyInstaller` `>=6.0.0` & `Inno Setup 6` | Standalone single-file `.exe` and Windows Setup Wizard |

Run the automated unit test suite via `pytest`:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

---

## License

Released under the **MIT License**.
