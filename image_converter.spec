# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# مسیرهای فونت و assets
assets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
fonts_path = os.path.join(assets_path, 'fonts')

# جمع‌آوری فایل‌های دیتا
added_files = []

if os.path.exists(fonts_path):
    for f in os.listdir(fonts_path):
        if f.endswith('.ttf') or f.endswith('.otf'):
            src = os.path.join(fonts_path, f)
            dst = os.path.join('assets', 'fonts')
            added_files.append((src, dst))

# اضافه کردن Pillow
added_files += collect_data_files('PIL')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'PIL',
        'PIL.Image',
        'PIL._imaging',
        'PIL._webp',
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'ui',
        'ui.splash_screen',
        'ui.main_window',
        'core',
        'core.converter',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
    ],
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
    name='ImageConverter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # بدون پنجره کنسول
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,  # آیکون برنامه
)