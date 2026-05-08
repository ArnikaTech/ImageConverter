#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil

def clean_build():
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for d in dirs_to_clean:
        if os.path.exists(d):
            shutil.rmtree(d)
    print("✅ پاکسازی انجام شد")

def build_exe():
    clean_build()
    
    # تشخیص آیکون
    icon_file = None
    for possible_icon in ['app_icon.ico', 'icon.ico', 'logo.ico']:
        if os.path.exists(possible_icon):
            icon_file = possible_icon
            break
    
    if not icon_file:
        print("⚠️ هیچ فایل آیکونی پیدا نشد. بدون آیکون بیلد میشه.")
    
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        '--onefile',
        '--windowed',
        '--name', 'ImageConverter',
        '--add-data', f'assets{os.pathsep}assets',
    ]
    
    if icon_file:
        cmd.extend(['--icon', icon_file])
        print(f"🎨 استفاده از آیکون: {icon_file}")
    
    cmd.append('main.py')
    
    print("🔨 در حال بیلد...")
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("✅ بیلد با موفقیت انجام شد!")
        print(f"📦 خروجی: {os.path.abspath('dist/ImageConverter.exe')}")
    else:
        print("❌ بیلد با خطا مواجه شد!")
        sys.exit(1)

if __name__ == '__main__':
    build_exe()