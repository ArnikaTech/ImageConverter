#!/usr/bin/env python3
"""
تبدیل لوگو به آیکون با سایزهای مختلف
لوگوی خودت رو بذار کنار این فایل و اسمش رو بذار logo.png
"""

from PIL import Image
import os

def convert_logo_to_ico(
    input_file="logo.png",
    output_file="app_icon.ico",
    sizes=[16, 24, 32, 48, 64, 128, 256]
):
    """
    تبدیل لوگو به فایل ICO با چندین سایز
    
    ورودی: فایل PNG با پس‌زمینه شفاف
    خروجی: فایل ICO با سایزهای مختلف برای ویندوز
    """
    
    if not os.path.exists(input_file):
        print(f"❌ فایل {input_file} پیدا نشد!")
        print("لطفاً لوگوی خودت رو با نام logo.png کنار این فایل قرار بده")
        return False
    
    try:
        # باز کردن تصویر اصلی
        img = Image.open(input_file)
        
        # اطمینان از حالت RGBA
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # ساخت لیست آیکون‌ها با سایزهای مختلف
        icon_sizes = []
        for size in sizes:
            # تغییر سایز با کیفیت بالا
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            icon_sizes.append(resized)
        
        # ذخیره به عنوان ICO
        icon_sizes[0].save(
            output_file,
            format='ICO',
            sizes=[(s, s) for s in sizes],
            append_images=icon_sizes[1:]
        )
        
        print(f"✅ آیکون با موفقیت ساخته شد: {output_file}")
        print(f"📐 سایزهای موجود: {', '.join(map(str, sizes))} پیکسل")
        
        # ساخت نسخه PNG هم برای لینوکس
        png_output = output_file.replace('.ico', '.png')
        img_256 = img.resize((256, 256), Image.Resampling.LANCZOS)
        img_256.save(png_output, 'PNG')
        print(f"✅ نسخه PNG هم ساخته شد: {png_output}")
        
        return True
        
    except Exception as e:
        print(f"❌ خطا در تبدیل: {e}")
        return False


if __name__ == "__main__":
    print("🎨 شروع تبدیل لوگو به آیکون...")
    print("-" * 40)
    
    # می‌تونی اسم فایل لوگو رو اینجا عوض کنی
    logo_file = "logo.png"
    
    # چک کردن فایل‌های احتمالی لوگو
    possible_names = ["logo.png", "logo.jpg", "logo.jpeg", "icon.png", "company_logo.png"]
    
    found = False
    for name in possible_names:
        if os.path.exists(name):
            logo_file = name
            found = True
            break
    
    if not found:
        print("❌ هیچ فایل لوگویی پیدا نشد!")
        print("لطفاً یکی از این فایل‌ها رو کنار اسکریپت قرار بده:")
        for name in possible_names:
            print(f"  - {name}")
        exit(1)
    
    print(f"📁 فایل لوگو: {logo_file}")
    convert_logo_to_ico(input_file=logo_file, output_file="app_icon.ico")