# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

# IMPORTANT:
# When this spec is located at my-timetable-next/build/timetable.spec,
# SPECPATH points to the build folder.
# Therefore the project root is the parent of SPECPATH.
ROOT = Path(SPECPATH).resolve().parent

block_cipher = None

datas = []

# Include data folder next to the EXE fallback resources
data_dir = ROOT / "data"
if data_dir.exists():
    for p in data_dir.rglob("*"):
        if p.is_file():
            datas.append((str(p), str(Path("data") / p.relative_to(data_dir).parent)))

# Include assets folder next to the EXE resources
assets_dir = ROOT / "assets"
if assets_dir.exists():
    for p in assets_dir.rglob("*"):
        if p.is_file():
            datas.append((str(p), str(Path("assets") / p.relative_to(assets_dir).parent)))

hiddenimports = []
hiddenimports += collect_submodules("PIL")

a = Analysis(
    [str(ROOT / "desktop" / "timetable.pyw")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="MyTimetableNext",
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
    icon=str(ROOT / "assets" / "logo.ico") if (ROOT / "assets" / "logo.ico").exists() else None,
)
