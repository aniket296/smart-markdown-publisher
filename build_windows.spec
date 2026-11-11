# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller specification for SmartMarkdownPublisher.exe."""

from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

project_root = Path(SPECPATH).resolve()

pygments_hidden = (
    collect_submodules("pygments.lexers")
    + collect_submodules("pygments.formatters")
    + collect_submodules("pygments.styles")
    + collect_submodules("markdown.extensions")
)

hidden_imports = [
    "fitz",
    "pymupdf",
    "PIL",
    "PIL.Image",
    "PIL.ImageDraw",
    "PIL.ImageTk",
    "PIL.ImageOps",
    "markdown",
    "yaml",
    "dotenv",
    "pygments",
    "pygments.lexers",
    "pygments.formatters",
    "pygments.styles",
] + pygments_hidden

a = Analysis(
    [str(project_root / "src" / "main.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        (str(project_root / "assets" / "app_icon.ico"), "assets"),
    ],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "onnxruntime",
        "pymupdf4llm",
        "pymupdf_layout",
        "networkx",
        "numpy",
        "scipy",
        "matplotlib",
        "pandas",
        "torch",
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="SmartMarkdownPublisher",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_root / "assets" / "app_icon.ico"),
)
