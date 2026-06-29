"""快速验证 OCR 效果 - 只测试第一张图片"""
import subprocess
import os
from pathlib import Path

IMG = Path(r"C:\Users\AUSU\Desktop\品牌\003323b2a98cc0aade231fe499091653.jpg")
TESSERACT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSDATA = os.path.expandvars(r"%USERPROFILE%\tesseract-tessdata")

env = os.environ.copy()
env["TESSDATA_PREFIX"] = TESSDATA

# 测试不同 PSM 模式
for psm in [3, 6]:
    result = subprocess.run(
        [TESSERACT, str(IMG), "stdout", "-l", "chi_sim", "--psm", str(psm)],
        capture_output=True, text=True, env=env, timeout=30, encoding="utf-8"
    )
    text = result.stdout.strip()
    print(f"=== PSM={psm} ({len(text)} chars) ===")
    print(text[:800])
    print("...\n")
