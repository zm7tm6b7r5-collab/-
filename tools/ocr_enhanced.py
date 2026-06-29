"""增强版 OCR - 针对 PPT 拍照图片的多策略预处理"""
import subprocess
import os
import sys
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance

# 强制 UTF-8 输出
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

IMG_DIR = Path(r"C:\Users\AUSU\Desktop\品牌")
TESSERACT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSDATA = os.path.expandvars(r"%USERPROFILE%\tesseract-tessdata")


def try_ocr(img: Image.Image, label: str, psm: int = 6) -> str:
    """对PIL图片进行OCR，返回文本"""
    tmp = IMG_DIR / f"_ocr_tmp_{label}.png"
    img.save(tmp)
    env = os.environ.copy()
    env["TESSDATA_PREFIX"] = TESSDATA
    try:
        r = subprocess.run(
            [TESSERACT, str(tmp), "stdout", "-l", "chi_sim+eng", "--psm", str(psm)],
            capture_output=True, text=True, env=env, timeout=30, encoding="utf-8"
        )
        text = r.stdout.strip()
    except Exception as e:
        text = f"[ERROR: {e}]"
    tmp.unlink()
    return text


# 测试前5张图片，输出写入文件
out_path = Path(r"C:\Users\AUSU\Documents\trae_projects\cc\tmp\ocr_test_results.txt")
images = sorted(IMG_DIR.glob("*.jpg"))[:5]

with open(out_path, "w", encoding="utf-8") as f:
    for img_path in images:
        f.write(f"\n{'='*60}\n")
        f.write(f"图片: {img_path.name}\n")
        img = Image.open(img_path)
        w, h = img.size
        f.write(f"尺寸: {w}x{h}\n")

        # 策略1: 原图
        t1 = try_ocr(img, "orig")
        f.write(f"\n[原图] {len(t1)} chars:\n{t1[:300]}\n")

        # 策略2: 灰度
        gray = img.convert("L")
        t2 = try_ocr(gray, "gray")
        f.write(f"\n[灰度] {len(t2)} chars:\n{t2[:300]}\n")

        # 策略3: 增强对比度 (最优)
        enh = ImageEnhance.Contrast(gray)
        hc = enh.enhance(2.5)
        hc = hc.filter(ImageFilter.SHARPEN)
        t3 = try_ocr(hc, "contrast")
        f.write(f"\n[高对比] {len(t3)} chars:\n{t3[:500]}\n")

        # 策略4: 放大2x + 增强对比
        if w < 2000:
            big = img.resize((w * 2, h * 2), Image.LANCZOS)
            big_gray = big.convert("L")
            big_enh = ImageEnhance.Contrast(big_gray).enhance(2.5)
            t4 = try_ocr(big_enh, "big_contrast")
            f.write(f"\n[放大+对比] {len(t4)} chars:\n{t4[:300]}\n")
        else:
            t4 = ""

        # 策略5: PSM 4
        enh2 = ImageEnhance.Contrast(gray).enhance(2.5)
        t5 = try_ocr(enh2, "contrast_psm4", psm=4)
        f.write(f"\n[PSM4] {len(t5)} chars:\n{t5[:300]}\n")

        results = [("原图", t1), ("灰度", t2), ("高对比", t3),
                    ("放大+对比", t4), ("PSM4", t5)]
        best = max(results, key=lambda x: len(x[1].strip()))
        f.write(f"\n>>> 最佳: {best[0]} ({len(best[1])} chars)\n")

print(f"Results written to: {out_path}")
