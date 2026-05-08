#!/usr/bin/env python3
"""
ساخت لوگوی حرفه‌ای برای برنامه
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import os

def create_modern_logo(size=512, company_name="شرکت نمونه", output_file="logo.png"):
    """
    ساخت لوگوی مدرن با طراحی گرادیانت
    
    Args:
        size: سایز لوگو (پیش‌فرض ۵۱۲)
        company_name: نام شرکت یا برنامه
        output_file: مسیر خروجی
    """
    
    # ساخت تصویر با پس‌زمینه شفاف
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    center = size // 2
    
    # ---------- دایره بیرونی (گرادیانت بنفش) ----------
    for i in range(size//2, size//4, -1):
        # محاسبه رنگ گرادیانت
        ratio = (i - size//4) / (size//4)
        r = int(108 + (30 - 108) * ratio)
        g = int(99 + (30 - 99) * ratio)
        b = int(255 + (60 - 255) * ratio)
        alpha = 255
        
        # دایره‌های متحدالمرکز
        draw.ellipse(
            [center - i, center - i, center + i, center + i],
            fill=(r, g, b, alpha)
        )
    
    # ---------- دایره داخلی (تیره) ----------
    inner_radius = size // 3
    draw.ellipse(
        [center - inner_radius, center - inner_radius,
         center + inner_radius, center + inner_radius],
        fill=(26, 26, 46, 255)
    )
    
    # ---------- حاشیه دایره داخلی ----------
    border_width = max(2, size // 128)
    draw.ellipse(
        [center - inner_radius - border_width, center - inner_radius - border_width,
         center + inner_radius + border_width, center + inner_radius + border_width],
        outline=(108, 99, 255, 255),
        width=border_width
    )
    
    # ---------- آیکون در مرکز ----------
    # یک شکل انتزاعی (مثل تبدیل)
    icon_size = inner_radius - size // 16
    
    # مستطیل چپ (تصویر ورودی)
    rect_margin = size // 8
    img_rect = [
        center - icon_size + rect_margin,
        center - icon_size//2,
        center - rect_margin,
        center + icon_size//2
    ]
    draw.rectangle(img_rect, fill=(108, 99, 255, 180), outline=(157, 78, 221, 255), width=3)
    
    # فلش تبدیل
    arrow_points = [
        (center - rect_margin, center - icon_size//4),
        (center + rect_margin, center - icon_size//4),
        (center + rect_margin, center - icon_size//2),
        (center + icon_size - rect_margin, center),
        (center + rect_margin, center + icon_size//2),
        (center + rect_margin, center + icon_size//4),
        (center - rect_margin, center + icon_size//4),
    ]
    draw.polygon(arrow_points, fill=(157, 78, 221, 255))
    
    # مستطیل راست (تصویر خروجی)
    out_rect = [
        center + icon_size - rect_margin * 3,
        center - icon_size//2,
        center + icon_size - rect_margin,
        center + icon_size//2
    ]
    draw.rectangle(out_rect, fill=(108, 99, 255, 180), outline=(157, 78, 221, 255), width=3)
    
    # ---------- ذرات تزئینی ----------
    for i in range(8):
        angle = (i / 8) * 2 * math.pi
        distance = size // 3 + size // 16
        x = center + int(math.cos(angle) * distance)
        y = center + int(math.sin(angle) * distance)
        particle_size = size // 32
        draw.ellipse(
            [x - particle_size, y - particle_size,
             x + particle_size, y + particle_size],
            fill=(108, 99, 255, 100)
        )
    
    # ---------- متن نام شرکت (اگر فونت در دسترس باشه) ----------
    try:
        # تلاش برای فونت فارسی
        font_paths = [
            "assets/fonts/Vazirmatn-Bold.ttf",
            "assets/fonts/Vazirmatn-Regular.ttf",
            "/usr/share/fonts/TTF/Vazirmatn-Bold.ttf",
            "C:\\Windows\\Fonts\\tahoma.ttf",
        ]
        
        font = None
        for fp in font_paths:
            if os.path.exists(fp):
                font = ImageFont.truetype(fp, size=size//10)
                break
        
        if font is None:
            font = ImageFont.load_default()
        
        # متن پایین لوگو
        text_bbox = draw.textbbox((0, 0), company_name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        text_x = center - text_width // 2
        text_y = size - size//6
        
        # پس‌زمینه نیمه‌شفاف برای متن
        padding = size // 32
        draw.rounded_rectangle(
            [text_x - padding, text_y - padding,
             text_x + text_width + padding, text_y + text_height + padding],
            radius=padding,
            fill=(26, 26, 46, 200)
        )
        
        # رسم متن
        draw.text((text_x, text_y), company_name, font=font, fill=(255, 255, 255, 255))
        
    except Exception as e:
        print(f"⚠️ نتونستم متن رو اضافه کنم: {e}")
    
    # ---------- ذخیره ----------
    # نسخه PNG با کیفیت بالا
    img.save(output_file, 'PNG')
    print(f"✅ لوگو ساخته شد: {output_file}")
    
    # نسخه‌های با سایز کوچکتر
    for s in [256, 128, 64, 48, 32]:
        small = img.resize((s, s), Image.Resampling.LANCZOS)
        small.save(f'logo_{s}.png', 'PNG')
    
    # نسخه ICO
    ico_sizes = [256, 128, 96, 64, 48, 40, 32, 24, 16]
    ico_images = [img.resize((s, s), Image.Resampling.LANCZOS) for s in ico_sizes]
    ico_images[0].save('app_icon.ico', format='ICO', sizes=[(s, s) for s in ico_sizes])
    print("✅ فایل ICO هم ساخته شد: app_icon.ico")
    
    return img


if __name__ == "__main__":
    # نام شرکت یا برنامه‌ات رو اینجا بذار
    COMPANY_NAME = "مبدل تصاویر"
    
    print("🎨 در حال ساخت لوگو...")
    create_modern_logo(
        size=512,
        company_name=COMPANY_NAME,
        output_file="logo.png"
    )
    print("🎉 تموم شد!")
    print("\nفایل‌های ساخته شده:")
    print("  📁 logo.png - لوگوی اصلی (512x512)")
    print("  📁 app_icon.ico - آیکون ویندوز")
    for s in [256, 128, 64, 48, 32]:
        print(f"  📁 logo_{s}.png - نسخه {s}x{s}")
