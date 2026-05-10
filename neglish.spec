# -*- mode: python ; coding: utf-8 -*-
# neglish.spec — PyInstaller build spec for Neglish v4.2
# Run:  pyinstaller neglish.spec
# Out:  dist/neglish.exe  (standalone, no Python required)

import os, glob

# Collect all stdlib .neg files so they're bundled inside the exe
stdlib_files = [(f, 'stdlib') for f in glob.glob('stdlib/*.neg')]

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=stdlib_files + [('negextension.ico', '.')],
    hiddenimports=['tkinter', 'tkinter.ttk', 'tkinter.messagebox',
                   'tkinter.filedialog', 'tkinter.colorchooser',
                   'tkinter.simpledialog', 'tkinter.font'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='neglish',
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
    icon='negextension.ico',
)
