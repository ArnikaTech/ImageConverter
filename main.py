import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontDatabase, QIcon
from ui.splash_screen import ModernSplashScreen
from ui.main_window import MainWindow


def get_resource_path(relative_path):
    """
    گرفتن مسیر منابع در حالت development و اجرایی
    """
    try:
        # PyInstaller یک دایرکتوری موقت می‌سازه
        base_path = sys._MEIPASS
    except AttributeError:
        # در حالت development
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)


def load_fonts():
    """بارگذاری فونت‌های فارسی"""
    font_family = None
    
    # مسیرهای احتمالی برای فونت
    possible_paths = [
        get_resource_path(os.path.join('assets', 'fonts')),
        os.path.join('assets', 'fonts'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'fonts'),
        os.path.join(os.path.expanduser('~'), '.local', 'share', 'fonts'),
        '/usr/share/fonts',
    ]

    font_files = [
        "Vazirmatn-Regular.ttf",
        "Vazirmatn.ttf",
        "Vazir.ttf",
    ]

    for fonts_dir in possible_paths:
        if not os.path.isdir(fonts_dir):
            continue

        for font_file in font_files:
            font_path = os.path.join(fonts_dir, font_file)
            if os.path.isfile(font_path):
                try:
                    font_id = QFontDatabase.addApplicationFont(font_path)
                    if font_id != -1:
                        font_families = QFontDatabase.applicationFontFamilies(font_id)
                        if font_families:
                            print(f"Font loaded: {font_families[0]}")
                            return font_families[0]
                except Exception as e:
                    print(f"Failed to load font {font_path}: {e}")

    # فونت پیش‌فرض
    backends = ["Vazirmatn", "Vazir", "Tahoma", "Arial", "Segoe UI"]
    for backend_font in backends:
        font = QFont(backend_font)
        if font.exactMatch():
            print(f"Using system font: {backend_font}")
            return backend_font

    return "Tahoma"


def main():
    app = QApplication(sys.argv)

    # راست‌چین کردن کل برنامه
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

    # بارگذاری فونت فارسی
    font_family = load_fonts()

    # تنظیم فونت پیش‌فرض برای کل برنامه
    default_font = QFont(font_family, 10)
    app.setFont(default_font)

    # نمایش Splash Screen
    splash = ModernSplashScreen()
    splash.show()
    app.processEvents()

    # ساخت پنجره اصلی
    window = MainWindow()

    # منتظر بمانیم تا اسپلش بسته شود
    def show_main_window():
        if splash._progress_value >= 100:
            window.show()
    splash._timer.timeout.connect(show_main_window)

        # تنظیم آیکون برنامه
    icon_path = get_resource_path('app_icon.ico')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    # یا از لوگوی ساخته شده
    logo_path = get_resource_path('logo.png')
    if os.path.exists(logo_path):
        window.setWindowIcon(QIcon(logo_path))

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
