from PIL import Image
import os
from typing import List, Dict, Optional, Callable


class ImageConverter:
    """کلاس ساده برای تبدیل فرمت‌های تصویری با Pillow"""

    # نگاشت فرمت‌های نمایشی به فرمت‌های Pillow
    FORMAT_MAP = {
        'PNG': 'PNG',
        'JPG': 'JPEG',
        'JPEG': 'JPEG',
        'BMP': 'BMP',
        'GIF': 'GIF',
        'TIFF': 'TIFF',
        'WEBP': 'WEBP'
    }

    SUPPORTED_FORMATS: List[str] = ['PNG', 'JPG', 'JPEG', 'BMP', 'GIF', 'TIFF', 'WEBP']

    def __init__(self):
        self.source_files: List[str] = []
        self.output_directory: str = ""

    def add_files(self, file_paths: List[str]) -> int:
        """اضافه کردن چندین فایل تصویری"""
        count = 0
        for path in file_paths:
            if os.path.isfile(path) and path not in self.source_files:
                self.source_files.append(path)
                count += 1
        return count

    def clear_files(self):
        """پاک کردن لیست فایل‌ها"""
        self.source_files.clear()

    def get_file_count(self) -> int:
        """تعداد فایل‌های انتخاب شده"""
        return len(self.source_files)

    def set_output_directory(self, directory: str) -> bool:
        """تنظیم پوشه خروجی"""
        if not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except OSError:
                return False
        self.output_directory = directory
        return True

    def convert_all(self, target_format: str, quality: int = 85,
                    progress_callback: Optional[Callable[[int], None]] = None) -> Dict[str, bool]:
        """
        تبدیل تمام تصاویر به فرمت جدید
        
        Args:
            target_format: فرمت مقصد (PNG, JPG, JPEG, BMP, GIF, TIFF, WEBP)
            quality: کیفیت خروجی (فقط برای JPG و WEBP)
            progress_callback: تابع callback برای گزارش پیشرفت
        
        Returns:
            دیکشنری از مسیر فایل منبع به وضعیت موفقیت/شکست
        """
        results = {}
        target_format_upper = target_format.upper().strip()

        # تبدیل فرمت نمایشی به فرمت Pillow
        pillow_format = self.FORMAT_MAP.get(target_format_upper)
        if pillow_format is None:
            print(f"Unsupported format: {target_format}")
            return results

        if not self.output_directory:
            if self.source_files:
                self.output_directory = os.path.dirname(self.source_files[0])
            else:
                return results

        # اطمینان از وجود پوشه خروجی
        os.makedirs(self.output_directory, exist_ok=True)

        # پسوند فایل خروجی
        if target_format_upper == 'JPG':
            output_extension = 'jpg'
        else:
            output_extension = target_format_upper.lower()

        total = len(self.source_files)

        for idx, source_path in enumerate(self.source_files):
            try:
                # بررسی وجود فایل منبع
                if not os.path.isfile(source_path):
                    print(f"Source file not found: {source_path}")
                    results[source_path] = False
                    if progress_callback:
                        progress_callback(int((idx + 1) / total * 100))
                    continue

                # ساخت مسیر خروجی
                base_name = os.path.splitext(os.path.basename(source_path))[0]
                dest_path = os.path.join(
                    self.output_directory,
                    f"{base_name}.{output_extension}"
                )

                # اگر فایل خروجی همون فایل ورودیه، رد می‌کنیم
                if os.path.abspath(source_path) == os.path.abspath(dest_path):
                    print(f"Skipping same file: {source_path}")
                    results[source_path] = False
                    if progress_callback:
                        progress_callback(int((idx + 1) / total * 100))
                    continue

                # باز کردن تصویر
                img = Image.open(source_path)

                # تبدیل مد رنگی برای JPEG (که پشتیبانی از کانال آلفا نداره)
                if pillow_format == 'JPEG':
                    if img.mode in ('RGBA', 'LA', 'P', 'PA'):
                        # ساخت تصویر جدید با پس‌زمینه سفید
                        if img.mode in ('RGBA', 'LA', 'PA'):
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            if img.mode == 'RGBA':
                                background.paste(img, mask=img.split()[3])
                            elif img.mode == 'LA':
                                background.paste(img, mask=img.split()[1])
                            elif img.mode == 'PA':
                                background.paste(img, mask=img.split()[1])
                            img = background
                        else:
                            img = img.convert('RGB')
                    elif img.mode not in ('RGB', 'L'):
                        img = img.convert('RGB')

                # تنظیمات ذخیره
                save_kwargs = {
                    'format': pillow_format,
                }

                if pillow_format == 'JPEG':
                    save_kwargs['quality'] = quality
                    save_kwargs['optimize'] = True
                elif pillow_format == 'PNG':
                    save_kwargs['optimize'] = True
                elif pillow_format == 'WEBP':
                    save_kwargs['quality'] = quality
                    save_kwargs['method'] = 6  # بهترین فشرده‌سازی

                # ذخیره تصویر
                img.save(dest_path, **save_kwargs)
                img.close()

                results[source_path] = True
                print(f"Success: {os.path.basename(source_path)} -> {os.path.basename(dest_path)}")

            except Exception as e:
                results[source_path] = False
                print(f"Error converting {source_path}: {str(e)}")

            # گزارش پیشرفت
            if progress_callback:
                progress_callback(int((idx + 1) / total * 100))

        return results

    def get_image_info(self, file_path: str) -> dict:
        """دریافت اطلاعات یک تصویر"""
        if not os.path.isfile(file_path):
            return {}

        try:
            img = Image.open(file_path)
            info = {
                'filename': os.path.basename(file_path),
                'format': img.format if img.format else 'نامشخص',
                'size': img.size,
                'mode': img.mode,
                'width': img.width,
                'height': img.height,
                'file_size': os.path.getsize(file_path)
            }
            img.close()
            return info
        except Exception as e:
            print(f"Error getting info for {file_path}: {str(e)}")
            return {}