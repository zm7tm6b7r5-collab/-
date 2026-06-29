import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from docx import Document
doc = Document(r'C:\Users\AUSU\Desktop\品牌管理课程笔记_优化版.docx')

current_q = ''
for p in doc.paragraphs:
    t = p.text.strip()
    if t.startswith('-- 高质量'):
        current_q = 'HIGH'
        print(f'\n=== {t} ===')
    elif t.startswith('-- 中等'):
        current_q = 'MED'
    elif t.startswith('-- 需核对'):
        current_q = 'LOW'
    elif current_q in ('HIGH', 'MED') and t and len(t) > 3:
        noisy = False
        for run in p.runs:
            if run.font.color and run.font.color.rgb:
                r = run.font.color.rgb
                if r[0] > 150 and r[1] < 120:
                    noisy = True
        label = "[NOISY]" if noisy else "[OK]  "
        print(f'  {label} {t[:120]}')
