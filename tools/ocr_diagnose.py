"""诊断图片质量 - 分析多张图片的属性和OCR可行性"""
import subprocess
import os
from pathlib import Path
from PIL import Image, ImageStat
import json

IMG_DIR = Path(r"C:\Users\AUSU\Desktop\品牌")
TESSERACT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSDATA = os.path.expandvars(r"%USERPROFILE%\tesseract-tessdata")

# 分析前5张图片
images = sorted(IMG_DIR.glob("*.jpg"))[:5]

for img_path in images:
    print(f"\n{'='*60}")
    print(f"图片: {img_path.name}")
    img = Image.open(img_path)
    print(f"尺寸: {img.size[0]}x{img.size[1]}, 模式: {img.mode}")

    # 分析亮度分布
    gray = img.convert("L")
    stat = ImageStat.Stat(gray)
    print(f"亮度: min={stat.extrema[0][0]:.0f}, max={stat.extrema[0][1]:.0f}, avg={stat.mean[0]:.0f}, std={stat.stddev[0]:.0f}")

    # 检查是否为拍照（EXIF信息）
    exif = img._getexif()
    if exif:
        print(f"EXIF: { {k:v for k,v in list(exif.items())[:5]} }")

    # 测试不同预处理方式
    env = os.environ.copy()
    env["TESSDATA_PREFIX"] = TESSDATA

    # 1. 直接用原图
    r = subprocess.run([TESSERACT, str(img_path), "stdout", "-l", "chi_sim+eng", "--psm", "4"],
                       capture_output=True, text=True, env=env, timeout=30, encoding="utf-8")
    t1 = r.stdout.strip()

    # 2. 灰度图
    gray_path = img_path.parent / f"_gray_{img_path.stem}.png"
    gray.save(gray_path)
    r = subprocess.run([TESSERACT, str(gray_path), "stdout", "-l", "chi_sim+eng", "--psm", "4"],
                       capture_output=True, text=True, env=env, timeout=30, encoding="utf-8")
    t2 = r.stdout.strip()
    gray_path.unlink()

    # 3. 二值化
    bw = gray.point(lambda x: 0 if x < 128 else 255)
    bw_path = img_path.parent / f"_bw_{img_path.stem}.png"
    bw.save(bw_path)
    r = subprocess.run([TESSERACT, str(bw_path), "stdout", "-l", "chi_sim+eng", "--psm", "4"],
                       capture_output=True, text=True, env=env, timeout=30, encoding="utf-8")
    t3 = r.stdout.strip()
    bw_path.unlink()

    print(f"原图 OCR ({len(t1)} chars): {t1[:200]}")
    print(f"灰度 OCR ({len(t2)} chars): {t2[:200]}")
    print(f"二值 OCR ({len(t3)} chars): {t3[:200]}")
