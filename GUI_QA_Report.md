# Live Desktop GUI QA, Visual Audit & Automation Report

**Project:** Smart Markdown-to-Print Desktop Publisher (`src/main.py`)  
**Audit Date:** 2026-11-12  
**Branch Verified:** `qa/verification-campaign` (`c4d8b91`) — unmodified application source code (`0` edits under `src/`)  
**Host / Display Environment:** Windows (`1920x1080` screen, `120 DPI` / **125% scaling**), Python 3.14 virtualenv (`.venv`)  
**Primary Artifacts:**
- Harness & Automation Runner: `_qa_gui_runner.py`
- System Context Map: `_qa_project_context.md`
- Complete Runtime UI Inventory: `_qa_ui_inventory.md` (`63` live Tkinter widgets + `5` OS `#32770` dialogs)
- Telemetry & Screenshots: `_qa_test_assets/` (`test_results.jsonl`, `defects.jsonl`, `performance.jsonl`, `raw_telemetry.jsonl`, `generated_outputs/`, `screenshots/`)

---

## 1. Executive Summary & Overall Health Score

The offline Markdown-to-Print engine (`compile_markdown`, `typeset_to_pdf_bytes`, `bind_folder_manuscript`), native file workflows (`Open .md`, `Save .md`, `Export Typeset PDF`), error handling (`Open File Error` on corrupted binary files), large-document handling (`1,500` lines compiled in `830.2 ms`), memory stability (`+0.0 MB` RSS delta over 15 rapid theme cycles), and keyboard focusability (`24` focusable traversal nodes, `0` blocked controls) are **functionally solid**.

However, live pixel and geometry inspection at `125% DPI scaling` identified **two High-severity layout/clipping defects** (plus two Medium/Low UI consistency issues):
1. At the default launch window (`1440x880` @ 125% DPI), the PDF Preview toolbar (`PdfPreviewPane`) clips **`Last >|`** down to `34px` (`"La"`) and pushes the **`Zoom:` label and zoom dropdown completely off-screen (`1x1px`, unmapped)** — leaving the user unable to zoom out (`75%` / `Fit Width`) when the `100%` page exceeds the `490px` preview viewport.
2. At the minimum enforced window size (`1060x680` @ 125% DPI), the non-wrapping top toolbar (`PublishingToolbar`) pushes the primary CTA button **`Export Typeset PDF`** and **`Callout [!NOTE]`** completely off-screen and clips **`Table`** (`60px` vs `110px`), while `PdfPreviewPane` also hides **`Next Page >`**, **`Last >|`**, and **`Zoom`** off-screen and sidebar notebook tabs clip to `"Outli"` / `"Document S"`.

### Weighted Scoring & Final Verdict (Section 9.2 Standard)
Applied weighting: `P0 = 5`, `P1 = 3`, `P2 = 1`. Blocked tests are NEVER counted as passed.

| Priority | Passed | Failed | Blocked / Not Run | Passed Weight | Failed Weight | Blocked Weight |
|---|---:|---:|---:|---:|---:|---:|
| **P0** (weight 5) | 8 | 0 | 0 | 40 | 0 | 0 |
| **P1** (weight 3) | 19 | 2 | 1 | 57 | 6 | 3 |
| **P2** (weight 1) | 4 | 0 | 1 | 4 | 0 | 1 |
| **Total** | **31** | **2** | **2** | **101** | **6** | **4** |

- **Total Weight:** `w_executed = 107`, `w_total = 111` (`35` scenarios)
- **Weighted Execution Pass Rate** = `101 / 107` = **`94.39%`**
- **Weighted Execution Coverage** = `107 / 111` = **`96.40%`**
- **Evidence-Adjusted QA Score** = `101 / 111` = **`90.99%`**
- **Severity Cap Applied:** **Yes — capped at `59`** due to `2` unresolved **High** severity defects (`DEF-GUI-001`, `DEF-GUI-002`).
- **Final Health Score:** **`59 / 100`**
- **Release Decision:** **HOLD / FIX REQUIRED BEFORE RELEASE** (responsive toolbar/preview-bar fixes required to prevent off-screen loss of primary CTA `Export Typeset PDF` and `Zoom` controls at declared `1060x680` and default `1440x880` @ 125% DPI).

---

## 2. Application Architecture & UI Inventory Summary

- **Desktop Shell:** `SmartMarkdownPublisherApp(tk.Tk)` (`src/gui/app.py`) with Windows Per-Monitor/System High-DPI awareness enabled (`enable_windows_high_dpi()`), default geometry `1440x880`, enforced `minsize(1060, 680)`.
- **Four UI Subsystems (`63` runtime widgets in `.` + `5` OS `#32770` dialogs):**
  1. `PublishingToolbar` (`src/gui/components/toolbar.py`): Row 1 (File actions, Snippet Insert buttons, primary `Export Typeset PDF` CTA) + Row 2 (`Theme`, `Page Size`, `Margins` `ttk.Combobox`es + `Font Size (pt)` `tk.Spinbox`).
  2. `OutlineSidebarPane` (`src/gui/components/outline_sidebar.py`): 2-tab `ttk.Notebook` (`Outline` hierarchical `Treeview` + `Document Setup` checkbuttons for cover/TOC/footer/header).
  3. `MarkdownEditorPane` (`src/gui/components/markdown_editor.py`): Line-number `Canvas` gutter + `Text` editor (`undo=True`, `wrap=WORD`) + vertical `Scrollbar` + live `Words | Est. Reading Time | Line, Col` footer.
  4. `PdfPreviewPane` (`src/gui/components/pdf_preview.py`): Navigation/Zoom bar (`|< First`, `< Prev Page`, `Page X of Y`, `Next Page >`, `Last >|`, `Zoom:`), scrollable `Canvas` rendering PyMuPDF pixmaps, and `Typeset in N ms` footer.
- **Full 63-widget inventory:** Documented in `_qa_ui_inventory.md`.

---

## 3. Window Geometry, DPI Scaling & Visual Inspection Matrix

Measured live at `120 DPI` (**125% scaling** on `1920x1080`):

| Dimension / State | Test ID | Measured Outer Rect | Responsive | Visual & Telemetry Observation | Result |
|---|---|---|---|---|---|
| Default Launch (`1440x880`) | `LIVE-001` / `GEOM-default_1440x880` | `1458x927` (`client 1440x880`) | Yes | Top toolbar fits; `PdfPreviewPane` clips **`Last >\|`** (`34px` vs `108px`, `"La"`) & hides **`Zoom:` + `zoom_combo`** off-right (`1x1px`); `Document Setup` header clips `"OPTIONS"`; long Outline headings clip right edge. | **FAILED** (`Clips=1` btn + hidden zoom) |
| Declared Min (`1060x680`) | `RESIZE-001` / `GEOM-min_1060x680` | `1078x727` | Yes | **Severe clipping:** `Export Typeset PDF` and `Callout [!NOTE]` pushed completely off-screen (`unmapped`); `Table` clipped (`60px` vs `110px`); `Next Page >`, `Last >\|`, `Zoom` hidden; sidebar tabs clip (`"Outli"`, `"Document S"`). | **FAILED** (`Clips=5`) |
| Below Minimum (`800x600`) | `RESIZE-002` | `1078x727` | Yes | `root.minsize(1060, 680)` strictly enforced. Same clipping as `1060x680`. | **PASSED** (minsize enforced) |
| Narrow-Tall (`1060x960`) | `RESIZE-003` | `1078x960` | Yes | Same horizontal toolbar & preview-bar clipping as `1060x680`; vertical height healthy. | **PASSED** (resize stable; horizontal clips remain) |
| Wide-Short (`1600x680`) | `RESIZE-004` | `1600x727` | Yes | Top toolbar + preview `Last >\|` + `Zoom` all fit cleanly at `1600px` width. | **PASSED** |
| Maximized (`1920x1080`) | `RESIZE-005` | `1938x1038` | Yes | All 63 widgets fit without clipping; clean 3-pane proportions. | **PASSED** |

---

## 4. Functional, End-to-End Modal & Edge-Case Execution Log

*(OS `#32770` dialogs triggered via live `button.invoke()` inside the running studio event loop and driven/captured externally via Win32 `EnumWindows` + `SendMessageW(WM_SETTEXT/BM_CLICK)` in `ModalDialogWatchdog`.)*

| Test ID | Priority | Category / Flow | Outcome | Observed Evidence |
|---|---|---|---|---|
| `LIVE-001` | P0 | App Startup & Showcase Typeset | **PASSED** | Window `HWND=2098200` up in `471.2 ms`, `RSS=83.79 MB`, `8` threads, `app_stderr.log` empty |
| `LIVE-OPEN-CANCEL` | P1 | `Open .md` -> OS `#32770` Cancel | **PASSED** | `"Open Markdown Manuscript"` (`50` controls) captured & dismissed; manuscript unchanged |
| `LIVE-OPEN-CORRUPT` | P0 | `Open .md` -> Corrupted Binary (`0xFF...`) | **PASSED** | Real OS `#32770` `"Open File Error"` popup verified (`dialog_open_error.png`); app stays responsive |
| `LIVE-OPEN-VALID` | P0 | `Open .md` -> `sample_spec.md` | **PASSED** | Title updated to `sample_spec.md`; preview rendered `2` pages (`screen_loaded_sample.png`) |
| `LIVE-SAVE-001` | P0 | `Save .md` -> OS `#32770` Save Dialog | **PASSED** | Saved `live_saved_sample.md` (`56 B`), verified exact UTF-8 content on disk |
| `LIVE-BOOK-DIALOG-OPEN` | P1 | `Bind Folder as Book...` -> OS Folder Picker | **PASSED** | `"Select Folder Containing Ordered Markdown Chapters (.md)"` (`44` controls) opened & cancelled |
| `LIVE-BOOK-FOLDER-SELECT` | P1 | Submit Folder Path in OS `IFileDialog` | **BLOCKED** | Windows COM `IFileDialog (FOS_PICKFOLDERS)` ignores `WM_SETTEXT` without interactive Shell selection |
| `FUNC-BOOK-BINDER-LOAD` | P1 | Multi-Chapter Book Binding Pipeline | **PASSED** | `bind_folder_manuscript` merged `01 -> 02 -> 10` (`Chapters 1, 2, 10` in order) & rendered `4` pages |
| `LIVE-EXPORT-001` | P0 | `Export Typeset PDF` -> OS Save + Ack | **PASSED** | Saved `live_exported_showcase.pdf` (`156,607 B`); PyMuPDF verified `4` pages, `6` TOC entries, `Page 1 of` footers |
| `FUNC-INSERT_*` (x5) | P1 | YAML / Bold / Code / Table / Callout Snippets | **PASSED** | All 5 toolbar actions inserted expected Markdown constructs into live editor |
| `FUNC-PROFILE-THEMES` | P0 | Switch All 4 Print Themes | **PASSED** | `Academic` (`360.8ms`), `Technical` (`361.7ms`), `Executive` (`364.9ms`), `Compact` (`362.9ms`) |
| `FUNC-THEME-VISUAL-DIFF` | P1 | Academic vs Technical Pixel Comparison | **PASSED** | `ImageChops.difference` bbox `(252, 56, 1419, 864)` proves live typography/accent color switch |
| `FUNC-OUTLINE-NAV` | P1 | Outline Treeview Heading Jump | **PASSED** | Selecting last heading jumped editor cursor to line `54` |
| `FUNC-SETUP-COVER-TOGGLE` | P0 | Document Setup `Generate Cover Page` Toggle | **PASSED** | Unchecking updated YAML `cover: false` and reduced live preview `3 -> 2` pages |
| `FUNC-PREVIEW-NAV-ZOOM` | P0 | Preview Pagination & `125%` Zoom | **PASSED** | `next=1`, `last=2`, `first=0`, rendered `125%` zoom image width = `652 px` |
| `PERF-LARGE-DOC-1500` | P1 | 1,500-Line Stress Manuscript | **PASSED** | Compiled & previewed in `830.2 ms`, scrollbar active `(0.000, 0.014)`, `24` pages |
| `EDGE-UNICODE-001` | P1 | Multilingual UTF-8 / Math / Special Symbols | **PASSED** | No crash; `66,158 B` PDF (`Page 1 of 1`) |
| `EDGE-EMPTY-001` | P1 | 0-Byte Empty Markdown Input | **PASSED** | No crash; `1,689 B` valid PDF (`Page 1 of 1`) |
| `EDGE-WRONG-EXT-001` | P2 | Non-Markdown `.xyz` UTF-8 File | **PASSED** | Valid `65,835 B` PDF rendered cleanly |
| `EDGE-DEEP-PATH-001` | P2 | Deep Path w/ Spaces & Symbols (`132` chars) | **PASSED** | Valid `65,839 B` PDF rendered cleanly |
| `STAB-STRESS-15X` | P1 | 15 Rapid Theme Re-Typeset Cycles | **PASSED** | `RSS 90.52 -> 90.52 MB` (`+0.00 MB` delta), `8` threads steady, no hangs |
| `A11Y-FOCUS-001` & `002` | P2 | Focusability & `Tab` Traversal | **PASSED** | `23` mapped interactive controls, `0` blocked; `24` distinct nodes traversed via `tk_focusNext()` |
| `ENV-OS-INPUT-BLOCKED` | P2 | External Win32 Cursor/Key Injection | **BLOCKED** | Session isolation blocks `SetCursorPos`/`mouse_event`/`keybd_event` on external HWND |

---

## 5. Requirements Traceability Matrix

| Req ID | Requirement Summary | Verification Scenarios | Result |
|---|---|---|---|
| `REQ-01` | Live 3-pane Studio (Outline/Setup, Editor w/ line numbers, PDF Preview) | `LIVE-001`, `GEOM-*`, `FUNC-OUTLINE-NAV`, `screen_*.png` | **PARTIAL** (`DEF-GUI-001/002/003` clipping) |
| `REQ-02` | Open / Save `.md` & Graceful Binary Error Popup | `LIVE-OPEN-CANCEL`, `LIVE-OPEN-CORRUPT`, `LIVE-OPEN-VALID`, `LIVE-SAVE-001` | **PASSED** |
| `REQ-03` | Bind Folder of Chapters as Book in Natural Numeric Order | `LIVE-BOOK-DIALOG-OPEN`, `FUNC-BOOK-BINDER-LOAD` (`LIVE-BOOK-FOLDER-SELECT` blocked at OS COM picker) | **PASSED** (core pipeline; OS folder commit blocked) |
| `REQ-04` | Markdown Parsing: YAML Frontmatter, Callouts, Code, Tables | `FUNC-INSERT_*`, `LIVE-EXPORT-001`, `EDGE-UNICODE-001` | **PASSED** |
| `REQ-05` | Print Profiles (`Academic`, `Technical`, `Executive`, `Compact`, Size, Margin, Pt) | `FUNC-PROFILE-THEMES`, `FUNC-THEME-VISUAL-DIFF` | **PASSED** |
| `REQ-06` | Document Setup Toggles (`Cover`, `TOC`, `Header`, `Footer`) synced w/ YAML | `FUNC-SETUP-COVER-TOGGLE`, `screen_document_setup.png` | **PASSED** (w/ `DEF-GUI-004` header label clip) |
| `REQ-07` | Export Publication PDF w/ Cover, Clickable TOC & `Page X of Y` | `LIVE-EXPORT-001` (`4` pages, `6` TOC bookmarks verified via PyMuPDF) | **PASSED** |
| `REQ-08` | Live Preview Pagination & Zoom Controls | `FUNC-PREVIEW-NAV-ZOOM` (`Zoom` usable programmatically; UI clipped per `DEF-GUI-002`) | **PARTIAL** (`DEF-GUI-002`) |
| `REQ-09` | Responsive Resize (`>= 1060x680` @ 125% DPI) & Memory Stability | `RESIZE-001..005`, `PERF-LARGE-DOC-1500`, `STAB-STRESS-15X` | **FAILED** (horizontal clipping at min/default sizes) |
| `REQ-10` | Keyboard Accessibility & Non-blocking Execution | `A11Y-FOCUS-001`, `A11Y-FOCUS-002`, `is_window_responsive` | **PASSED** |

---

## 6. Consolidated Defect Register

### DEF-001 (`DEF-GUI-001`) — Primary Export CTA & Toolbar Controls Clipped / Pushed Off-Screen at Minimum Size (`1060x680`)
- **Severity:** **High** | **Category:** Visual / Responsive Layout
- **Affected Module & Screen:** `src/gui/components/toolbar.py` -> Main Studio Top Toolbar
- **Evidence:** `GEOM-min_1060x680` (`_qa_test_assets/telemetry/defects.jsonl`), `_qa_test_assets/screenshots/resizing/min_1060x680.png`, `narrow_tall.png`
- **Root Cause:** `top_row` packs 9 buttons (`File:` group + `Insert:` group) left-to-right alongside `Export Typeset PDF` (`pack(side=tk.RIGHT)`) on a single non-wrapping row whose total required width is `1394px` at 125% DPI (`root reqwidth = 1928px`), exceeding `minsize(1060, 680)`.
- **Actual Result:** At `1060x680` and `1060x960`, **`Export Typeset PDF`** and **`Callout [!NOTE]`** are pushed completely off-screen (`unmapped_offscreen_button`), and **`Table`** is clipped (`width=60px` vs `reqwidth=110px`).
- **Expected Result:** Primary CTA (`Export Typeset PDF`) remains permanently visible and unclipped across all supported window widths (`>= 1060px`), and toolbar action buttons wrap or compact cleanly.

### DEF-002 (`DEF-GUI-002`) — PDF Preview `Last >|` Clipped & `Zoom` Controls Pushed Off-Screen at Default (`1440x880`) and Minimum (`1060x680`)
- **Severity:** **High** | **Category:** Visual / Responsive Layout / Usability
- **Affected Module & Screen:** `src/gui/components/pdf_preview.py` -> Right `PdfPreviewPane` Navigation Bar
- **Evidence:** `_qa_ui_inventory.md` (#55–#57), `GEOM-default_1440x880` (`width=34` vs `reqwidth=108`), `GEOM-min_1060x680`, `launch_default.png`, `theme_technical.png`, `screen_loaded_sample.png`
- **Root Cause:** `nav_bar` packs 5 fixed-width navigation controls (`|< First`, `< Prev Page`, `Page X of Y`, `Next Page >`, `Last >|` = `535px+` plus padding = `715px reqwidth`) on `LEFT` and `Zoom:` + `zoom_combo` on `RIGHT` inside a single row, whereas `PdfPreviewPane` receives ~`505px` at default `1440x880` (weight=3 of `TPanedwindow`).
- **Actual Result:** At default `1440x880`, **`Last >|`** renders truncated as **`"La"`** (`34px`) and **`Zoom:` + `100%` combobox** disappear completely off-screen (`1x1px`, `viewable=False`) — preventing mouse users from zooming down to fit the page inside the `490px` viewport. At `1060x680`, **`Next Page >`** is also lost.
- **Expected Result:** Navigation buttons (`|<`, `<`, `Page X/Y`, `>`, `>|`) and `Zoom` selector remain 100% visible, unclipped, and usable at both `1440x880` and `1060x680`.

### DEF-003 (`DEF-GUI-003`) — Outline Sidebar Tabs & Treeview Headings Clip Horizontally at Default / Minimum Widths
- **Severity:** **Medium** | **Category:** Layout / Readability
- **Affected Module & Screen:** `src/gui/components/outline_sidebar.py` -> Left `OutlineSidebarPane`
- **Evidence:** `widget_inventory.json` (#28–#35), `launch_default.png`, `min_1060x680.png`, `screen_document_setup.png`
- **Actual Result:** Left sidebar width (`231px` at `1440x880`, narrower at `1060x680`) is smaller than its requested `300px`: in `Document Setup`, `"FRONTMATTER & LAYOUT OPTIONS"` (`reqwidth=264px`) clips `"OPTIONS"`; in `Outline`, long section titles truncate without horizontal scroll or tooltip; at `1060x680`, tab labels clip (`"Outli"`, `"Document S"`).
- **Expected Result:** Wrap or shorten section title text cleanly, enforce sensible pane `minsize`, and provide horizontal scrollbar or compact tab titles (`Setup`) so labels never truncate.

### DEF-004 (`DEF-GUI-004`) — `Font Size (pt)` Uses Unstyled `tk.Spinbox` Next to `ttk.Combobox` Controls
- **Severity:** **Low** | **Category:** Visual Consistency
- **Affected Module & Screen:** `src/gui/components/toolbar.py` (`font_spin`)
- **Evidence:** `widget_inventory.json` (#26 `Spinbox`), `theme_technical.png`
- **Actual Result:** `Font Size (pt)` renders as a slightly shorter `24px`-high classic `tk.Spinbox` beside `30px`-high `ttk.Combobox` widgets (`Theme`, `Page Size`, `Margins`).
- **Expected Result:** Replace with `ttk.Spinbox` (matching height/border styling) for uniform toolbar alignment.

---

## 7. Stability, Memory & Performance Measurements

Recorded cleanly in `_qa_test_assets/telemetry/performance.jsonl` (`0` stderr errors in `app_stderr.log`):
- **Cold Launch & Initial Showcase Typeset:** `471.2 ms` (`RSS = 83.79 MB`, `8` threads)
- **Single-Document Theme Switch Response:** `360.8 – 364.9 ms` end-to-end including UI pump
- **1,500-Line Stress Compilation & 24-Page Render:** `830.24 ms` (`v_scroll = (0.000, 0.014)`)
- **15 Rapid Consecutive Theme-Switch Re-Typeset Cycles:** `RSS 90.52 MB -> 90.52 MB` (**`+0.00 MB` net delta**, zero thread leak, zero queue backlog)
- **Post-Resize Runtime Health:** `83.80 MB RSS`, `8` threads, Win32 `SendMessageTimeoutW` responsive (`True`)

---

## 8. Generated Output Validation

- **Markdown Save (`_qa_test_assets/generated_outputs/live_saved_sample.md`):** `56 B`, exact UTF-8 match of editor buffer verified after closing OS Save As dialog.
- **Exported Typeset PDF (`_qa_test_assets/generated_outputs/live_exported_showcase.pdf`):** `156,607 B`; independently opened and verified with PyMuPDF (`fitz.open`):
  - **Page Count:** `4` pages (Page 1 Cover + Pages 2–4 Content)
  - **Clickable PDF Outline (`get_toc()`):** `6` hierarchical bookmark entries
  - **Headers & Footers:** Verified `"Page 1 of 3"` (content numbering) present on body pages, zero blank/corrupted pages.

---

## 9. Known Environmental Limitations

- **OS Pointer / Keystroke Injection (`ENV-OS-INPUT-BLOCKED`):** Windows desktop session isolation blocks programmatic `SetCursorPos`, `mouse_event`, and `keybd_event` against external HWNDs (`SetCursorPos(100,100)` stayed at `327, 658`). Core application responsiveness and resizing were audited via external `subprocess.Popen` + Win32 `MoveWindow`/`ShowWindow`/`SendMessageTimeoutW`; all `#32770` OS file/save/error modal workflows were executed cleanly via live `button.invoke()` inside the studio event loop paired with our external Win32 `ModalDialogWatchdog`.
- **COM `IFileDialog (FOS_PICKFOLDERS)` Path Entry (`LIVE-BOOK-FOLDER-SELECT`):** Windows folder picker ignores `WM_SETTEXT` without interactive Shell selection; opening/cancelling the real OS dialog was verified live, and `bind_folder_manuscript()` + multi-chapter GUI rendering was verified end-to-end via `FUNC-BOOK-BINDER-LOAD`.

---

## 10. Phased Remediation Blueprint (Prioritized Plan — Awaiting Approval)

Fixes have NOT been applied yet per QA Phase 10 protocol. Upon your approval, remediation can proceed sequentially across 3 crisp Sub-Phases with full pytest + live GUI re-verification after each step:

1. **Sub-Phase 1 — Fix Top Toolbar Overflow & Primary CTA Visibility (`src/gui/components/toolbar.py`) [`DEF-001`, `DEF-004`]:**
   - Anchor `Export Typeset PDF` cleanly in a non-clipped right column (`grid` layout or compact button widths/icons) AND wrap or split `FILE:` and `INSERT:` button groups onto responsive rows/compact labels (`Callout`, `Book...`, tighter padding) so 100% of toolbar controls fit comfortably at `1060px` width @ 125% DPI.
   - Replace classic `tk.Spinbox` with `ttk.Spinbox` aligned to `ttk.Combobox` height.
   - Add automated geometry regression check confirming `0` clipped/unmapped toolbar buttons at `1060x680` and `1440x880`.
2. **Sub-Phase 2 — Fix PDF Preview Navigation & Zoom Bar + Default Fit-Width (`src/gui/components/pdf_preview.py`) [`DEF-002`]:**
   - Compact navigation labels (`|<`, `<`, `Page X/Y`, `>`, `>|`) or stack nav + zoom into a 2-tier compact header / flexible `grid` so all pagination buttons AND `Zoom:` dropdown remain 100% visible even when `PdfPreviewPane` is `360–505px` wide (`1060x680` and `1440x880`).
   - Add `"Fit Width"` option (or sensible default width scaling) so the preview page never clips horizontally by default while preserving `50%–200%` manual zoom.
3. **Sub-Phase 3 — Fix Outline & Document Setup Sidebar Clipping (`src/gui/components/outline_sidebar.py`, `src/gui/app.py`) [`DEF-003`]:**
   - Shorten tab title `"Document Setup"` -> `"Setup"` (or add padding/min pane width on `TPanedwindow`), set `wraplength` on `"FRONTMATTER & LAYOUT OPTIONS"`, and add horizontal scrollbar (`xscrollcommand`) to the Outline `Treeview`.
   - Re-run `_qa_gui_runner.py` + `pytest`, inspect before/after screenshots, confirm `0` failed checks and `100%` clean geometry before updating `GUI_QA_Report.md`.
