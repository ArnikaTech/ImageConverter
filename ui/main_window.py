from PyQt6.QtWidgets import (
    QMainWindow, QMenu, QToolBar, QStatusBar,
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QSlider, QProgressBar, QFileDialog, QMessageBox,
    QListWidget, QListWidgetItem, QFrame, QSplitter, QComboBox,
    QAbstractItemView, QApplication
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QAction, QFont
from core.converter import ImageConverter
import os


def format_file_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} بایت"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} کیلوبایت"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} مگابایت"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.converter = ImageConverter()
        self.selected_format = "PNG"
        self._conversion_in_progress = False

        self._app_font = QApplication.font()
        self._app_font_family = self._app_font.family()

        self.setWindowTitle("مبدل تصاویر")
        self.setMinimumSize(896, 672)

        self._center_on_screen()
        self._setup_menu_bar()
        self._setup_toolbar()
        self._setup_statusbar()
        self._setup_central_widget()
        self._apply_global_stylesheet()

    def _center_on_screen(self):
        screen = self.screen()
        if screen:
            center = screen.availableGeometry().center()
            geo = self.frameGeometry()
            geo.moveCenter(center)
            self.move(geo.topLeft())

    def _setup_menu_bar(self):
        menu_bar = self.menuBar()
        menu_bar.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        menu_bar.setFont(self._app_font)

        file_menu = QMenu("فایل", self)
        file_menu.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        file_menu.setFont(QFont(self._app_font_family, 10))

        add_action = QAction("افزودن تصاویر...", self)
        add_action.setShortcut("Ctrl+O")
        add_action.triggered.connect(self._add_images)
        file_menu.addAction(add_action)

        add_folder_action = QAction("افزودن از پوشه...", self)
        add_folder_action.setShortcut("Ctrl+Shift+O")
        add_folder_action.triggered.connect(self._add_folder_images)
        file_menu.addAction(add_folder_action)

        file_menu.addSeparator()

        clear_action = QAction("پاک کردن لیست", self)
        clear_action.triggered.connect(self._clear_list)
        file_menu.addAction(clear_action)

        file_menu.addSeparator()

        convert_action = QAction("شروع تبدیل...", self)
        convert_action.setShortcut("Ctrl+Enter")
        convert_action.triggered.connect(self._start_conversion)
        file_menu.addAction(convert_action)

        file_menu.addSeparator()

        exit_action = QAction("خروج", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        menu_bar.addMenu(file_menu)

        help_menu = QMenu("راهنما", self)
        help_menu.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        help_menu.setFont(QFont(self._app_font_family, 10))

        about_action = QAction("درباره برنامه", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

        menu_bar.addMenu(help_menu)

    def _setup_toolbar(self):
        toolbar = QToolBar("نوار ابزار اصلی", self)
        toolbar.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        toolbar.setFont(QFont(self._app_font_family, 10))
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        add_btn = QPushButton("+ افزودن تصاویر")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self._add_images)
        toolbar.addWidget(add_btn)

        toolbar.addSeparator()

        format_label = QLabel("فرمت خروجی:")
        format_label.setStyleSheet("color: #e0e0e0; font-size: 13px; background: transparent;")
        toolbar.addWidget(format_label)

        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "JPG", "WEBP", "BMP", "TIFF"])
        self.format_combo.setCurrentText("PNG")
        self.format_combo.currentTextChanged.connect(
            lambda f: setattr(self, 'selected_format', f)
        )
        self.format_combo.setMinimumWidth(100)
        toolbar.addWidget(self.format_combo)

        toolbar.addSeparator()

        convert_btn = QPushButton("شروع تبدیل")
        convert_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        convert_btn.setObjectName("convertBtn")
        convert_btn.clicked.connect(self._start_conversion)
        toolbar.addWidget(convert_btn)

    def _setup_statusbar(self):
        self.status_bar = QStatusBar()
        self.status_bar.setFont(QFont(self._app_font_family, 10))
        self.status_bar.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.status_bar.showMessage("آماده به کار | برای شروع، تصاویر خود را اضافه کنید")
        self.setStatusBar(self.status_bar)

        self.file_count_label = QLabel("۰ تصویر انتخاب شده")
        self.file_count_label.setStyleSheet(
            "color: #6C63FF; font-size: 12px; background: transparent; padding: 0 12px;"
        )
        self.status_bar.addPermanentWidget(self.file_count_label)

        self.format_status_label = QLabel("خروجی: PNG")
        self.format_status_label.setStyleSheet(
            "color: #9D4EDD; font-size: 12px; background: transparent; padding: 0 12px;"
        )
        self.status_bar.addPermanentWidget(self.format_status_label)

    def _setup_central_widget(self):
        central = QWidget()
        central.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(18, 18, 18, 18)
        self.setCentralWidget(central)

        # ---------------------- پنل بالایی: آمار ----------------------
        stats_panel = QFrame()
        stats_panel.setObjectName("statsPanel")
        stats_layout = QHBoxLayout(stats_panel)
        stats_layout.setSpacing(12)
        stats_layout.setContentsMargins(16, 12, 16, 12)

        self.total_files_label = QLabel("کل تصاویر: ۰")
        self.total_files_label.setFont(QFont("Vazirmatn", 11))
        stats_layout.addWidget(self.total_files_label)

        self.total_size_label = QLabel("حجم کل: ۰ بایت")
        self.total_size_label.setFont(QFont("Vazirmatn", 11))
        stats_layout.addWidget(self.total_size_label)

        self.success_count_label = QLabel("موفق: ۰")
        self.success_count_label.setFont(QFont("Vazirmatn", 11))
        self.success_count_label.setStyleSheet("color: #4CAF50; background: transparent;")
        stats_layout.addWidget(self.success_count_label)

        self.fail_count_label = QLabel("ناموفق: ۰")
        self.fail_count_label.setFont(QFont("Vazirmatn", 11))
        self.fail_count_label.setStyleSheet("color: #F44336; background: transparent;")
        stats_layout.addWidget(self.fail_count_label)

        stats_layout.addStretch()
        main_layout.addWidget(stats_panel)

        # ---------------------- اسپلیتر اصلی ----------------------
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(2)

        # ---------- پنل راست: لیست تصاویر ----------
        list_group = QGroupBox("تصاویر انتخاب شده")
        list_group.setFont(QFont("Vazirmatn", 12))
        list_group.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        list_layout = QVBoxLayout(list_group)
        list_layout.setSpacing(8)
        list_layout.setContentsMargins(10, 16, 10, 10)

        self.image_list = QListWidget()
        self.image_list.setFont(QFont("Vazirmatn", 10))
        self.image_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.image_list.setAlternatingRowColors(True)
        self.image_list.setSpacing(2)
        self.image_list.setMinimumWidth(400)
        list_layout.addWidget(self.image_list)

        list_btn_layout = QHBoxLayout()
        list_btn_layout.setSpacing(8)

        remove_btn = QPushButton("حذف انتخاب شده")
        remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_btn.setObjectName("secondaryBtn")
        remove_btn.clicked.connect(self._remove_selected)
        list_btn_layout.addWidget(remove_btn)

        clear_all_btn = QPushButton("پاک کردن همه")
        clear_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_all_btn.setObjectName("secondaryBtn")
        clear_all_btn.clicked.connect(self._clear_list)
        list_btn_layout.addWidget(clear_all_btn)

        list_btn_layout.addStretch()
        list_layout.addLayout(list_btn_layout)

        splitter.addWidget(list_group)

        # ---------- پنل چپ: تنظیمات و پیشرفت ----------
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(12)
        right_layout.setContentsMargins(0, 0, 0, 0)

        settings_group = QGroupBox("تنظیمات تبدیل")
        settings_group.setFont(QFont("Vazirmatn", 12))
        settings_group.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setSpacing(14)
        settings_layout.setContentsMargins(14, 16, 14, 14)

        fmt_layout = QHBoxLayout()
        fmt_label = QLabel("فرمت خروجی:")
        fmt_label.setFont(QFont("Vazirmatn", 11))
        fmt_layout.addWidget(fmt_label)
        fmt_layout.addStretch()
        self.settings_format_combo = QComboBox()
        self.settings_format_combo.addItems(["PNG", "JPG", "WEBP", "BMP", "TIFF"])
        self.settings_format_combo.setCurrentText("PNG")
        self.settings_format_combo.currentTextChanged.connect(self._on_format_changed)
        self.settings_format_combo.setMinimumWidth(140)
        fmt_layout.addWidget(self.settings_format_combo)
        settings_layout.addLayout(fmt_layout)

        quality_layout = QHBoxLayout()
        quality_layout.setSpacing(10)
        quality_label = QLabel("کیفیت:")
        quality_label.setFont(QFont("Vazirmatn", 11))
        quality_layout.addWidget(quality_label)

        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setRange(10, 100)
        self.quality_slider.setValue(90)
        self.quality_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.quality_slider.setTickInterval(10)
        quality_layout.addWidget(self.quality_slider, 1)

        self.quality_value_label = QLabel("۹۰%")
        self.quality_value_label.setFont(QFont("Vazirmatn", 11))
        self.quality_value_label.setMinimumWidth(50)
        self.quality_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.quality_value_label.setStyleSheet(
            "color: #e0e0e0; background: #1a1a2e; border: 1px solid #3a3a5c; "
            "border-radius: 6px; padding: 4px 10px;"
        )
        self.quality_slider.valueChanged.connect(
            lambda v: self.quality_value_label.setText(f"{v}%")
        )
        quality_layout.addWidget(self.quality_value_label)
        settings_layout.addLayout(quality_layout)

        right_layout.addWidget(settings_group)

        progress_group = QGroupBox("پیشرفت تبدیل")
        progress_group.setFont(QFont("Vazirmatn", 12))
        progress_group.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        progress_layout = QVBoxLayout(progress_group)
        progress_layout.setSpacing(10)
        progress_layout.setContentsMargins(14, 16, 14, 14)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFont(QFont("Vazirmatn", 10))
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("آماده تبدیل")
        self.progress_bar.setMinimumHeight(28)
        progress_layout.addWidget(self.progress_bar)

        self.progress_detail_label = QLabel("منتظر شروع تبدیل...")
        self.progress_detail_label.setFont(QFont("Vazirmatn", 10))
        self.progress_detail_label.setStyleSheet("color: #9090aa; background: transparent;")
        self.progress_detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(self.progress_detail_label)

        right_layout.addWidget(progress_group)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.add_btn_main = QPushButton("+ افزودن تصاویر")
        self.add_btn_main.setFont(QFont("Vazirmatn", 11))
        self.add_btn_main.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn_main.clicked.connect(self._add_images)
        btn_layout.addWidget(self.add_btn_main)

        self.convert_btn = QPushButton("شروع تبدیل")
        self.convert_btn.setFont(QFont("Vazirmatn", 11))
        self.convert_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.convert_btn.setObjectName("convertBtnLarge")
        self.convert_btn.clicked.connect(self._start_conversion)
        self.convert_btn.setMinimumHeight(44)
        btn_layout.addWidget(self.convert_btn)

        right_layout.addLayout(btn_layout)
        right_layout.addStretch()

        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        main_layout.addWidget(splitter, 1)

    def _add_images(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "انتخاب تصاویر", "",
            "تصاویر (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp);;همه فایل‌ها (*)"
        )
        if files:
            self._process_added_files(files)

    def _add_folder_images(self):
        folder = QFileDialog.getExistingDirectory(self, "انتخاب پوشه")
        if folder:
            supported_ext = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp')
            image_files = []
            for root, _, files in os.walk(folder):
                for f in files:
                    if f.lower().endswith(supported_ext):
                        image_files.append(os.path.join(root, f))
            if image_files:
                self._process_added_files(image_files)
            else:
                QMessageBox.information(self, "اطلاعات", "هیچ تصویری در این پوشه یافت نشد.")

    def _process_added_files(self, files):
        count = self.converter.add_files(files)
        for f in files:
            info = self.converter.get_image_info(f)
            if info:
                size_str = format_file_size(info.get('file_size', 0))
                dim_str = f"{info.get('width', '?')}x{info.get('height', '?')}"
                item_text = (
                    f"  {info['filename']}  |  {dim_str}  |  "
                    f"{size_str}  |  {info.get('format', '?')}"
                )
                item = QListWidgetItem(item_text)
                item.setToolTip(f"مسیر: {f}")
                self.image_list.addItem(item)

        self._update_stats()
        self.status_bar.showMessage(f"{count} تصویر با موفقیت اضافه شد")
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("آماده تبدیل")

    def _remove_selected(self):
        selected_items = self.image_list.selectedItems()
        if not selected_items:
            return

        indices = [self.image_list.row(item) for item in selected_items]
        indices.sort(reverse=True)

        for idx in indices:
            self.image_list.takeItem(idx)
            if idx < len(self.converter.source_files):
                self.converter.source_files.pop(idx)

        self._update_stats()

    def _clear_list(self):
        self.image_list.clear()
        self.converter.clear_files()
        self._update_stats()
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("آماده تبدیل")
        self.progress_detail_label.setText("منتظر شروع تبدیل...")
        self.status_bar.showMessage("لیست تصاویر پاک شد")

    def _on_format_changed(self, fmt):
        self.selected_format = fmt
        self.format_combo.setCurrentText(fmt)
        self.format_status_label.setText(f"خروجی: {fmt}")

    def _start_conversion(self):
        if self._conversion_in_progress:
            return

        if self.converter.get_file_count() == 0:
            QMessageBox.warning(self, "هشدار", "لطفاً ابتدا حداقل یک تصویر اضافه کنید.")
            return

        output_dir = QFileDialog.getExistingDirectory(self, "انتخاب پوشه خروجی")
        if not output_dir:
            return

        self._conversion_in_progress = True
        self.converter.set_output_directory(output_dir)
        quality = self.quality_slider.value()
        target_format = self.selected_format

        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("در حال تبدیل...")
        self.progress_detail_label.setText(
            f"تبدیل به {target_format} با کیفیت {quality}%"
        )
        self.status_bar.showMessage("در حال تبدیل تصاویر...")
        self.convert_btn.setEnabled(False)
        self.add_btn_main.setEnabled(False)

        total_files = self.converter.get_file_count()

        def update_progress(value):
            self.progress_bar.setValue(value)
            self.progress_bar.setFormat(f"{value}%")
            processed = min(int(value * total_files / 100), total_files)
            self.progress_detail_label.setText(
                f"در حال پردازش... {processed} از {total_files}"
            )
            QApplication.processEvents()

        def finish_conversion(success_count, fail_count):
            self._conversion_in_progress = False
            self.convert_btn.setEnabled(True)
            self.add_btn_main.setEnabled(True)
            self.progress_bar.setValue(100)
            self.progress_bar.setFormat("اتمام تبدیل")
            self.progress_detail_label.setText(
                f"تبدیل به پایان رسید. {success_count} موفق، {fail_count} ناموفق"
            )
            self.success_count_label.setText(f"موفق: {success_count}")
            self.fail_count_label.setText(f"ناموفق: {fail_count}")
            self.status_bar.showMessage(
                f"تبدیل تمام شد | موفق: {success_count} | ناموفق: {fail_count}"
            )

        def do_convert():
            try:
                results = self.converter.convert_all(
                    target_format,
                    quality=quality,
                    progress_callback=update_progress
                )
                success_count = sum(1 for v in results.values() if v)
                fail_count = sum(1 for v in results.values() if not v)
            except Exception as e:
                success_count = 0
                fail_count = self.converter.get_file_count()
                print(f"Conversion error: {str(e)}")
            
            finish_conversion(success_count, fail_count)

        QTimer.singleShot(300, do_convert)

    def _update_stats(self):
        count = self.converter.get_file_count()
        self.file_count_label.setText(f"{count} تصویر انتخاب شده")

        total_size = 0
        for f in self.converter.source_files:
            if os.path.exists(f):
                total_size += os.path.getsize(f)

        self.total_files_label.setText(f"کل تصاویر: {count}")
        self.total_size_label.setText(f"حجم کل: {format_file_size(total_size)}")
        self.success_count_label.setText("موفق: ۰")
        self.fail_count_label.setText("ناموفق: ۰")

    def _show_about(self):
        QMessageBox.about(
            self, "درباره برنامه",
            "مبدل تصویر نسخه 2.0.0\n\n"
            "ابزار حرفه‌ای تبدیل فرمت‌های تصویری\n"
            "با پشتیبانی از تبدیل گروهی\n\n"
            "فرمت‌های پشتیبانی شده:\n"
            "PNG, JPG, JPEG, WEBP, BMP, GIF, TIFF\n\n"
            "طراح و توسعه‌دهنده: حمید رضا بردرانی\n"
            "تماس: 09363765475\n\n"
            "شرکت فناوری مهندسی آرنیکا"
        )

    def _apply_global_stylesheet(self):
        stylesheet = """
            QMainWindow {
                background-color: #1a1a2e;
            }

            QWidget {
                background-color: #1a1a2e;
                color: #e0e0e0;
            }

            QFrame#statsPanel {
                background-color: #1e1e36;
                border: 1px solid #2a2a4a;
                border-radius: 10px;
            }

            QFrame#statsPanel QLabel {
                background: transparent;
                padding: 4px 12px;
                border-radius: 6px;
                background-color: #252545;
            }

            QMenuBar {
                background-color: #15152a;
                color: #e0e0e0;
                font-size: 14px;
                padding: 4px 8px;
                border-bottom: 2px solid #6C63FF;
            }

            QMenuBar::item {
                background: transparent;
                padding: 6px 14px;
                border-radius: 6px;
                margin: 2px 2px;
            }

            QMenuBar::item:selected {
                background-color: #6C63FF;
                color: #ffffff;
            }

            QMenu {
                background-color: #1e1e36;
                color: #e0e0e0;
                border: 1px solid #3a3a5c;
                border-radius: 8px;
                padding: 6px 4px;
                font-size: 13px;
            }

            QMenu::item {
                padding: 8px 30px 8px 16px;
                border-radius: 4px;
                margin: 2px 4px;
            }

            QMenu::item:selected {
                background-color: #6C63FF;
                color: #ffffff;
            }

            QMenu::separator {
                height: 1px;
                background-color: #3a3a5c;
                margin: 4px 10px;
            }

            QToolBar {
                background-color: #15152a;
                border-bottom: 1px solid #2a2a4a;
                spacing: 8px;
                padding: 6px 10px;
            }

            QToolBar QPushButton {
                background-color: #252545;
                color: #e0e0e0;
                border: 1px solid #3a3a5c;
                border-radius: 6px;
                padding: 8px 18px;
                font-size: 13px;
                font-weight: bold;
            }

            QToolBar QPushButton:hover {
                background-color: #6C63FF;
                color: #ffffff;
                border-color: #6C63FF;
            }

            QToolBar QPushButton#convertBtn {
                background-color: #6C63FF;
                border-color: #6C63FF;
                color: #ffffff;
            }

            QToolBar QPushButton#convertBtn:hover {
                background-color: #7B73FF;
            }

            QToolBar QComboBox {
                background-color: #252545;
                color: #e0e0e0;
                border: 1px solid #3a3a5c;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
                min-width: 100px;
            }

            QToolBar QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: left center;
                width: 24px;
                border-left: 1px solid #3a3a5c;
            }

            QToolBar QComboBox QAbstractItemView {
                background-color: #1e1e36;
                color: #e0e0e0;
                selection-background-color: #6C63FF;
                border: 1px solid #3a3a5c;
                border-radius: 4px;
            }

            QSplitter::handle {
                background-color: #2a2a4a;
            }

            QSplitter::handle:hover {
                background-color: #6C63FF;
            }

            QGroupBox {
                background-color: #1e1e36;
                border: 2px solid #6C63FF;
                border-radius: 10px;
                margin-top: 18px;
                padding: 18px 14px 14px 14px;
                font-size: 14px;
                font-weight: bold;
                color: #e0e0e0;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top right;
                padding: 4px 16px;
                background-color: #6C63FF;
                color: #ffffff;
                border-radius: 6px;
                margin-right: 14px;
            }

            QListWidget {
                background-color: #1a1a2e;
                color: #e0e0e0;
                border: 1px solid #2a2a4a;
                border-radius: 8px;
                padding: 6px;
                font-size: 12px;
                outline: none;
            }

            QListWidget::item {
                padding: 10px 12px;
                border-radius: 6px;
                margin: 2px 2px;
                background-color: #222240;
            }

            QListWidget::item:alternate {
                background-color: #1e1e38;
            }

            QListWidget::item:selected {
                background-color: #6C63FF;
                color: #ffffff;
            }

            QListWidget::item:hover {
                background-color: #2a2a50;
            }

            QComboBox {
                background-color: #252545;
                color: #e0e0e0;
                border: 1px solid #3a3a5c;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
            }

            QComboBox:hover {
                border-color: #6C63FF;
            }

            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: left center;
                width: 28px;
                border-left: 1px solid #3a3a5c;
            }

            QComboBox QAbstractItemView {
                background-color: #1e1e36;
                color: #e0e0e0;
                selection-background-color: #6C63FF;
                border: 1px solid #3a3a5c;
                border-radius: 6px;
                padding: 4px;
            }

            QComboBox QAbstractItemView::item {
                padding: 8px 12px;
                border-radius: 4px;
            }

            QPushButton {
                background-color: #6C63FF;
                color: #ffffff;
                border: 1px solid #6C63FF;
                border-radius: 8px;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #7B73FF;
                border-color: #7B73FF;
            }

            QPushButton:pressed {
                background-color: #5A52E0;
                border-color: #5A52E0;
            }

            QPushButton:disabled {
                background-color: #3a3a5c;
                border-color: #3a3a5c;
                color: #8888aa;
            }

            QPushButton#secondaryBtn {
                background-color: #252545;
                color: #e0e0e0;
                border: 1px solid #3a3a5c;
                font-size: 12px;
                padding: 8px 16px;
            }

            QPushButton#secondaryBtn:hover {
                background-color: #F44336;
                border-color: #F44336;
                color: #ffffff;
            }

            QPushButton#convertBtnLarge {
                background-color: #6C63FF;
                font-size: 15px;
                padding: 12px 32px;
            }

            QPushButton#convertBtnLarge:hover {
                background-color: #7B73FF;
            }

            QSlider::groove:horizontal {
                background: #2a2a4a;
                height: 10px;
                border-radius: 5px;
            }

            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #9D4EDD, stop:1 #6C63FF);
                border: 2px solid #ffffff;
                width: 20px;
                height: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }

            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #B57EDD, stop:1 #7B73FF);
            }

            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6C63FF, stop:1 #9D4EDD);
                border-radius: 5px;
            }

            QProgressBar {
                background-color: #2a2a4a;
                border: 1px solid #3a3a5c;
                border-radius: 8px;
                text-align: center;
                color: #e0e0e0;
                font-size: 12px;
                font-weight: bold;
            }

            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6C63FF, stop:0.5 #9D4EDD, stop:1 #C77DFF);
                border-radius: 7px;
            }

            QStatusBar {
                background-color: #15152a;
                color: #b0b0c0;
                border-top: 2px solid #6C63FF;
                font-size: 13px;
                padding: 4px 12px;
            }

            QStatusBar QLabel {
                background: transparent;
                color: #b0b0c0;
            }

            QScrollBar:vertical {
                background: #1a1a2e;
                width: 10px;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical {
                background: #3a3a5c;
                border-radius: 5px;
                min-height: 30px;
            }

            QScrollBar::handle:vertical:hover {
                background: #6C63FF;
            }

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QMessageBox {
                background-color: #1e1e36;
                color: #e0e0e0;
            }

            QMessageBox QLabel {
                color: #e0e0e0;
                background: transparent;
            }

            QMessageBox QPushButton {
                min-width: 90px;
                min-height: 34px;
            }
        """
        self.setStyleSheet(stylesheet)
