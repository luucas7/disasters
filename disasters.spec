# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the Global Disasters Dashboard.

Builds a single self-contained executable from ``launch.py`` that bundles the
Python runtime, all dependencies, the cleaned data and the web assets.

Build it on the target OS (PyInstaller does not cross-compile):

    pip install -r requirements.txt pyinstaller
    pyinstaller disasters.spec --noconfirm

The executable is written to ``dist/disasters`` (``dist/disasters.exe`` on
Windows).
"""

from PyInstaller.utils.hooks import collect_all

# Static resources shipped alongside the code. The (src, dest) pairs mirror the
# project layout so get_project_paths()/get_base_path() resolve them at runtime.
datas = [
    ("assets", "assets"),
    ("data", "data"),
]
binaries = []
hiddenimports = []

# Dash, Plotly and dash_ag_grid ship JavaScript/JSON package data that must be
# collected explicitly, otherwise the frozen app fails to serve its frontend.
for package in ("dash", "dash_ag_grid", "plotly", "pandas"):
    pkg_datas, pkg_binaries, pkg_hidden = collect_all(package)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hidden

a = Analysis(
    ["launch.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # selenium is only used for optional scraping, which the packaged app
    # never performs; excluding it keeps the executable smaller.
    excludes=["selenium"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="disasters",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
