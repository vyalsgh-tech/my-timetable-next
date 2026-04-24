# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

project_root = Path.cwd()

a = Analysis(
    [str(project_root / "desktop" / "timetable.pyw")],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        (str(project_root / "assets" / "logo.ico"), "assets"),
        (str(project_root / "assets" / "logo.png"), "assets"),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="MyTimetableNext",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=str(project_root / "assets" / "logo.ico"),
)
