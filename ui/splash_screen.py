from PyQt6.QtWidgets import QSplashScreen, QApplication
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QLinearGradient, QBrush, QPen, QRadialGradient
import math


class ModernSplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._pixmap = QPixmap(520, 440)
        self._pixmap.fill(Qt.GlobalColor.transparent)
        self.setPixmap(self._pixmap)

        self._progress_value = 0
        self._status_text = "در حال بارگذاری..."
        self._animation_angle = 0
        self._pulse_radius = 0

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_progress)
        self._timer.start(35)

        self._animation_timer = QTimer(self)
        self._animation_timer.timeout.connect(self._update_animation)
        self._animation_timer.start(50)

        self._statuses = [
            "بارگذاری موتور پردازش تصویر...",
            "آماده‌سازی رابط کاربری...",
            "تنظیم تم و استایل‌ها...",
            "بارگذاری ماژول‌های تبدیل...",
            "راه‌اندازی نهایی..."
        ]

        # گرفتن فونت پیش‌فرض برنامه
        self._app_font = QApplication.font()

    def _update_animation(self):
        self._animation_angle = (self._animation_angle + 3) % 360
        self._pulse_radius = 48 + math.sin(self._animation_angle * math.pi / 180) * 8
        self.repaint()

    def _update_progress(self):
        self._progress_value += 1
        if self._progress_value > 100:
            self._progress_value = 100
            self._timer.stop()
            self._animation_timer.stop()
            self.close()

        idx = min(self._progress_value // 20, len(self._statuses) - 1)
        self._status_text = self._statuses[idx]
        self.repaint()

    def drawContents(self, painter: QPainter):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(0, 0, 520, 440)

        # گرادیانت پس‌زمینه
        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        gradient.setColorAt(0.0, QColor("#0F0C29"))
        gradient.setColorAt(0.5, QColor("#1a1a2e"))
        gradient.setColorAt(1.0, QColor("#1a0533"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawRoundedRect(rect, 24, 24)

        # دایره‌های تزئینی
        circles = [
            (QPointF(430, 60), 70, QColor(108, 99, 255, 12)),
            (QPointF(80, 350), 55, QColor(157, 78, 221, 10)),
            (QPointF(470, 360), 40, QColor(108, 99, 255, 15)),
            (QPointF(60, 80), 35, QColor(157, 78, 221, 8)),
            (QPointF(440, 190), 25, QColor(255, 255, 255, 5)),
        ]

        for center, radius, color in circles:
            painter.setBrush(color)
            painter.drawEllipse(center, radius, radius)

        # دایره‌های کوچک اضافی
        for i, angle in enumerate([30, 120, 210, 300]):
            rad = angle * math.pi / 180
            cx = 160 + 100 * math.cos(rad)
            cy = 140 + 100 * math.sin(rad)
            painter.setBrush(QColor(255, 255, 255, 6 + i * 2))
            painter.drawEllipse(QPointF(cx, cy), 8, 8)

        # لوگوی دایره‌ای با پالس
        logo_center = QPointF(260, 130)

        # حلقه بیرونی پالس
        pulse_alpha = int(40 * (1 - (self._pulse_radius - 48) / 8))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        pen = QPen(QColor(108, 99, 255, max(0, pulse_alpha)), 2)
        painter.setPen(pen)
        painter.drawEllipse(logo_center, self._pulse_radius, self._pulse_radius)

        # دایره اصلی لوگو
        painter.setPen(Qt.PenStyle.NoPen)
        logo_gradient = QRadialGradient(logo_center, 50)
        logo_gradient.setColorAt(0.0, QColor("#9D4EDD"))
        logo_gradient.setColorAt(0.7, QColor("#6C63FF"))
        logo_gradient.setColorAt(1.0, QColor("#2D1B69"))
        painter.setBrush(QBrush(logo_gradient))
        painter.drawEllipse(logo_center, 50, 50)

        # حاشیه لوگو
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor("#ffffff"), 2.5))
        painter.drawEllipse(logo_center, 50, 50)

        # متن داخل لوگو
        font_logo = QFont(self._app_font)
        font_logo.setPointSize(24)
        font_logo.setBold(True)
        painter.setFont(font_logo)
        painter.setPen(QColor("#ffffff"))
        painter.drawText(QRectF(logo_center.x() - 45, logo_center.y() - 22, 90, 44),
                        Qt.AlignmentFlag.AlignCenter, "IMG")

        # عنوان برنامه
        font_title = QFont(self._app_font)
        font_title.setPointSize(22)
        font_title.setBold(True)
        painter.setFont(font_title)
        title_gradient = QLinearGradient(0, 195, 520, 195)
        title_gradient.setColorAt(0.0, QColor("#e0e0e0"))
        title_gradient.setColorAt(0.5, QColor("#ffffff"))
        title_gradient.setColorAt(1.0, QColor("#b0b0c0"))
        painter.setPen(QPen(QBrush(title_gradient), 1))
        painter.drawText(QRectF(0, 200, 520, 40), Qt.AlignmentFlag.AlignCenter, "مبدل تصاویر")

        # زیرنویس
        font_subtitle = QFont(self._app_font)
        font_subtitle.setPointSize(10)
        painter.setFont(font_subtitle)
        painter.setPen(QColor("#9090aa"))
        painter.drawText(QRectF(0, 235, 520, 22), Qt.AlignmentFlag.AlignCenter,
                        "تبدیل حرفه‌ای فرمت‌های تصویری")

        # شماره نسخه
        font_ver = QFont(self._app_font)
        font_ver.setPointSize(9)
        font_ver.setWeight(QFont.Weight.Light)
        painter.setFont(font_ver)
        painter.setPen(QColor("#7070aa"))
        painter.drawText(QRectF(0, 255, 520, 20), Qt.AlignmentFlag.AlignCenter, "نسخه 2.0.0")

        # Progress Bar
        bar_x, bar_y, bar_w, bar_h = 80, 320, 360, 10
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#1f1f3d"))
        painter.drawRoundedRect(QRectF(bar_x, bar_y, bar_w, bar_h), 5, 5)

        # براقی پس‌زمینه بار
        painter.setBrush(QColor(255, 255, 255, 5))
        painter.drawRoundedRect(QRectF(bar_x, bar_y, bar_w, bar_h / 2), 5, 5)

        fill_width = (self._progress_value / 100.0) * bar_w
        if fill_width > 0:
            bar_gradient = QLinearGradient(bar_x, bar_y, bar_x + bar_w, bar_y)
            bar_gradient.setColorAt(0.0, QColor("#6C63FF"))
            bar_gradient.setColorAt(0.5, QColor("#9D4EDD"))
            bar_gradient.setColorAt(1.0, QColor("#C77DFF"))
            painter.setBrush(QBrush(bar_gradient))
            painter.drawRoundedRect(QRectF(bar_x, bar_y, fill_width, bar_h), 5, 5)

            # نقطه نورانی روی progress bar
            if fill_width > 10:
                glow = QRadialGradient(bar_x + fill_width, bar_y + bar_h / 2, 14)
                glow.setColorAt(0.0, QColor(255, 255, 255, 100))
                glow.setColorAt(1.0, QColor(255, 255, 255, 0))
                painter.setBrush(QBrush(glow))
                painter.drawEllipse(QPointF(bar_x + fill_width, bar_y + bar_h / 2), 12, 12)

        # درصد پیشرفت
        font_pct = QFont(self._app_font)
        font_pct.setPointSize(9)
        font_pct.setBold(True)
        painter.setFont(font_pct)
        painter.setPen(QColor("#c0c0d0"))
        painter.drawText(QRectF(bar_x, bar_y + 14, bar_w, 20),
                        Qt.AlignmentFlag.AlignCenter, f"{self._progress_value}%")

        # متن وضعیت
        font_status = QFont(self._app_font)
        font_status.setPointSize(10)
        painter.setFont(font_status)
        painter.setPen(QColor("#b0b0c0"))
        painter.drawText(QRectF(0, 365, 520, 25),
                        Qt.AlignmentFlag.AlignCenter, self._status_text)

        # خطوط تزئینی پایین
        painter.setPen(QPen(QColor("#6C63FF"), 0.5))
        for i in range(3):
            y = 395 + i * 4
            alpha = 80 - i * 25
            painter.setPen(QPen(QColor(108, 99, 255, max(10, alpha)), 0.5))
            margin = 60 + i * 30
            painter.drawLine(int(margin), y, int(520 - margin), y)

    def mousePressEvent(self, event):
        pass