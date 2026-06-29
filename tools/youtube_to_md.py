#!/usr/bin/env python3
"""
YouTube → Markdown 转换工具
============================

功能：输入 YouTube URL，自动下载中文字幕（优先手动字幕，
      回退到自动生成），清理时间戳，合并为通顺段落，
      输出结构化 Markdown 文件。

用法：
    python youtube_to_md.py <YouTube_URL>

    python youtube_to_md.py https://www.youtube.com/watch?v=xxxxx
    python youtube_to_md.py https://youtu.be/xxxxx

输出：
    <视频标题>.md  — 当前目录下生成

依赖：
    yt-dlp（已通过 pip 安装）

作者：AI 辅助生成
日期：2026-06-16
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# ── Windows GBK 编码兼容 ──
if sys.platform == "win32":
    # 将 stdout/stderr 切换到 UTF-8，解决 emoji 打印报错
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        # Python < 3.7 fallback
        import io
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace"
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, encoding="utf-8", errors="replace"
        )


# ── 配置 ────────────────────────────────────────────────
# 字幕语言优先级（按顺序尝试：中文手动 → 中文自动 → 英文）
SUBTITLE_LANGS = [
    "zh-Hans",   # 简体中文（手动字幕）
    "zh",        # 中文（手动字幕，无简繁区分）
    "zh-Hant",   # 繁体中文（手动字幕）
    "en",        # 英文（手动字幕）
]

# 自动字幕回退（当所有手动语言都无字幕时）
AUTO_SUBTITLE_LANGS = [
    "zh-Hans",   # 简体中文自动字幕
    "zh",        # 中文自动字幕
    "en",        # 英文自动字幕
]

# 合并字幕行时，两句之间的最大时间间隔（秒）
# 超过此间隔，视为新段落
MAX_GAP_SECONDS = 3.0

# 输出目录（留空 = 当前目录）
OUTPUT_DIR = ""


# ── 工具函数 ────────────────────────────────────────────

def run_ytdlp(url: str, args: list, timeout: int = 120) -> subprocess.CompletedProcess:
    """运行 yt-dlp 命令，统一处理错误。"""
    cmd = ["yt-dlp", "--no-warnings"] + args + [url]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        encoding="utf-8",
        errors="replace",
    )
    return result


def get_video_info(url: str) -> dict:
    """
    获取视频基本信息（不下载视频本身）。

    返回：
        {
            "title": str,
            "description": str,
            "upload_date": "YYYYMMDD",
            "channel": str,
            "duration": int (秒),
            "url": str,
        }
    """
    print("📡 获取视频信息...")
    result = run_ytdlp(url, [
        "--dump-json",
        "--skip-download",
        "--no-playlist",
    ])

    if result.returncode != 0:
        print(f"❌ 获取视频信息失败：\n{result.stderr}")
        sys.exit(1)

    import json
    info = json.loads(result.stdout)

    return {
        "title": info.get("title", "未知标题"),
        "description": info.get("description", ""),
        "upload_date": info.get("upload_date", ""),
        "channel": info.get("channel", info.get("uploader", "未知频道")),
        "duration": info.get("duration", 0),
        "url": info.get("webpage_url", url),
    }


def match_lang_in_list(lang: str, available: list) -> str:
    """
    在可用字幕列表中匹配语言。

    手动字幕代码：zh-Hans, en, zh
    自动字幕代码：zh-Hans-en, en-de （格式：目标-源）

    匹配规则：手动字幕精确匹配；自动字幕检查是否以目标语言开头。
    返回匹配到的实际语言代码，未匹配返回 None。
    """
    for code in available:
        if code == lang:
            return code
    # 自动字幕模糊匹配：zh-Hans 匹配 zh-Hans-en, zh-Hans-de 等
    for code in available:
        if code.startswith(lang + "-"):
            return code
    return None


def pick_subtitle_lang(url: str) -> tuple:
    """
    用 yt-dlp --list-subs 获取可用字幕，按优先级选择。

    返回：
        (lang_code, is_auto)  如 ("zh-Hans", False)
        没有字幕则返回 (None, False)

    与 list_subtitles 不同，本函数直接解析 --list-subs 输出，
    正确处理自动字幕的复合代码（如 zh-Hans-en）。
    """
    result = run_ytdlp(url, [
        "--list-subs",
        "--skip-download",
        "--no-playlist",
    ])

    if result.returncode != 0:
        print(f"[WARN] 获取字幕列表失败：\n{result.stderr}")
        return (None, False)

    output = result.stdout

    # 分离手动字幕和自动字幕段落
    manual_codes = []
    auto_codes = []
    current_section = None

    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue

        if "Available automatic captions" in line:
            current_section = "auto"
            continue
        elif "Available subtitles" in line:
            current_section = "manual"
            continue
        elif "has no subtitles" in line or line.startswith("Language"):
            continue

        # 数据行：首列为语言代码
        if current_section and "vtt" in line.lower():
            code = line.split()[0]
            if current_section == "manual":
                manual_codes.append(code)
            else:
                auto_codes.append(code)

    print(f"   📋 手动字幕：{manual_codes if manual_codes else '无'}")
    print(f"   📋 自动字幕：{auto_codes[:5]}{'...' if len(auto_codes) > 5 else ''}（共 {len(auto_codes)} 种）")

    # 按优先级匹配手动字幕
    for lang in SUBTITLE_LANGS:
        matched = match_lang_in_list(lang, manual_codes)
        if matched:
            return (matched, False)

    # 回退到自动字幕
    for lang in AUTO_SUBTITLE_LANGS:
        matched = match_lang_in_list(lang, auto_codes)
        if matched:
            return (matched, True)

    return (None, False)


def download_subtitle(url: str, lang: str, is_auto: bool) -> str:
    """
    下载指定语言的字幕，返回 VTT 文本内容。

    参数：
        url: 视频 URL
        lang: 语言代码，如 "zh-Hans"
        is_auto: 是否下载自动生成字幕

    返回：
        VTT 格式的字幕文本（str）
    """
    kind = "自动生成" if is_auto else "手动上传"
    print(f"📥 下载字幕：{lang}（{kind}）...")

    # 用临时目录存放字幕文件
    with tempfile.TemporaryDirectory() as tmpdir:
        args = [
            "--skip-download",
            "--no-playlist",
            "--write-subs" if not is_auto else "--write-auto-subs",
            "--sub-lang", lang,
            "--sub-format", "vtt",
            "--convert-subs", "vtt",
            "--output", os.path.join(tmpdir, "%(title)s.%(ext)s"),
        ]
        result = run_ytdlp(url, args, timeout=300)

        if result.returncode != 0:
            print(f"❌ 字幕下载失败：\n{result.stderr}")
            sys.exit(1)

        # 找到下载的 .vtt 文件
        vtt_files = list(Path(tmpdir).glob("*.vtt"))
        if not vtt_files:
            print("❌ 未找到下载的字幕文件（.vtt）")
            sys.exit(1)

        vtt_path = vtt_files[0]
        with open(vtt_path, "r", encoding="utf-8", errors="replace") as f:
            vtt_content = f.read()

    return vtt_content


# ── VTT 字幕解析 ────────────────────────────────────────

def parse_vtt(vtt_text: str) -> list:
    """
    解析 VTT 格式字幕，返回字幕片段列表。

    VTT 格式示例：
        WEBVTT
        Kind: captions
        Language: zh-Hans

        00:00:00.000 --> 00:00:04.500 align:start position:0%
        大家好<00:00:00.120>

        00:00:04.500 --> 00:00:08.200
        今天我们来讨论<00:00:04.680>这个话题

    返回：
        [
            {"start": 0.0, "end": 4.5, "text": "大家好"},
            {"start": 4.5, "end": 8.2, "text": "今天我们来讨论这个话题"},
            ...
        ]
    """
    segments = []

    # 匹配时间戳行：00:00:00.000 --> 00:00:04.500
    time_pattern = re.compile(
        r"(\d{2}):(\d{2}):(\d{2})\.(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})\.(\d{3})"
    )

    # 匹配行内的对齐标记和位置
    cue_settings_pattern = re.compile(r"\s+align:\w+\s+position:\d+%")

    lines = vtt_text.splitlines()

    i = 0
    # 跳过头部（WEBVTT + 元数据行）
    while i < len(lines):
        line = lines[i].strip()
        if time_pattern.match(line):
            break
        i += 1

    # 解析每个字幕块
    while i < len(lines):
        line = lines[i].strip()
        time_match = time_pattern.match(line)

        if time_match:
            # 计算起止时间（秒）
            start = (
                int(time_match.group(1)) * 3600
                + int(time_match.group(2)) * 60
                + int(time_match.group(3))
                + int(time_match.group(4)) / 1000
            )
            end = (
                int(time_match.group(5)) * 3600
                + int(time_match.group(6)) * 60
                + int(time_match.group(7))
                + int(time_match.group(8)) / 1000
            )

            # 读取下一行（文本内容）
            i += 1
            text_parts = []
            while i < len(lines):
                next_line = lines[i].strip()
                # 空行或下一个时间戳 → 结束当前块
                if not next_line or time_pattern.match(next_line):
                    break
                text_parts.append(next_line)
                i += 1

            raw_text = " ".join(text_parts)
            clean_text = clean_subtitle_text(raw_text)

            if clean_text:
                segments.append({
                    "start": start,
                    "end": end,
                    "text": clean_text,
                })
        else:
            i += 1

    return segments


def clean_subtitle_text(text: str) -> str:
    """
    清理字幕文本：
    - 移除 <c>、</c> 等 HTML 标签
    - 移除行内时间戳 <00:00:00.120>
    - 移除对齐标记
    - 合并多余空白
    """
    # 移除 HTML 标签（如 <c.bg_transparent>、</c>、<b> 等）
    text = re.sub(r"<[^>]+>", "", text)
    # 移除行内时间戳 <00:00:00.120>
    text = re.sub(r"<\d{2}:\d{2}:\d{2}\.\d{3}>", "", text)
    # 移除 &nbsp;
    text = text.replace("&nbsp;", " ")
    # 合并多余空白
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ── 字幕合并为段落 ──────────────────────────────────────

def merge_segments(segments: list, max_gap: float = MAX_GAP_SECONDS) -> list:
    """
    将字幕片段合并为段落。

    合并规则：
    1. 同一条字幕内的行 → 自然合并
    2. 不同字幕块间，时间间隔 ≤ max_gap 秒 → 合并到同一段落
    3. 时间间隔 > max_gap 秒 → 新段落
    4. 以句号、问号、感叹号结尾的片段后，即使时间连续也优先断句

    返回：
        [
            {"start": 0.0, "text": "段落文本..."},
            {"start": 10.5, "text": "段落文本..."},
            ...
        ]
    """
    if not segments:
        return []

    paragraphs = []
    current_para = {
        "start": segments[0]["start"],
        "text": segments[0]["text"],
    }
    last_end = segments[0]["end"]

    for seg in segments[1:]:
        gap = seg["start"] - last_end

        # 判断是否需要新段落
        new_paragraph = False

        # 规则1：时间间隔过大
        if gap > max_gap:
            new_paragraph = True

        # 规则2：上一段以完整句结尾（大概率是自然断句点）
        if current_para["text"].rstrip().endswith(("。", "？", "！", ".", "?", "!")):
            new_paragraph = True

        # 规则3：上一段已经比较长（>200字），给读者喘息
        if len(current_para["text"]) > 200:
            new_paragraph = True

        if new_paragraph:
            paragraphs.append(current_para)
            current_para = {
                "start": seg["start"],
                "text": seg["text"],
            }
        else:
            # 合并到当前段落
            # 避免重复空格/标点
            if current_para["text"].endswith(("。", "？", "！", ".", "?", "!", "，", ",", "；", ";")):
                current_para["text"] += seg["text"]
            else:
                current_para["text"] += seg["text"]

        last_end = seg["end"]

    # 别忘了最后一段
    paragraphs.append(current_para)

    return paragraphs


# ── Markdown 生成 ───────────────────────────────────────

def seconds_to_timestamp(seconds: float) -> str:
    """秒数 → mm:ss 格式。"""
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"


def date_to_readable(ymd: str) -> str:
    """YYYYMMDD → YYYY-MM-DD。"""
    if len(ymd) == 8:
        return f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:8]}"
    return ymd


def generate_markdown(info: dict, paragraphs: list, lang: str, is_auto: bool) -> str:
    """
    生成 Markdown 文档。
    """
    title = info["title"]
    safe_title = re.sub(r'[\\/*?:"<>|]', "", title).strip()
    # 限制文件名长度
    if len(safe_title) > 80:
        safe_title = safe_title[:80]

    # ── 文件头（YAML frontmatter） ──
    md = "---\n"
    md += f"title: \"{title}\"\n"
    md += f"source: \"{info['url']}\"\n"
    md += f"channel: \"{info['channel']}\"\n"
    if info["upload_date"]:
        md += f"date: {date_to_readable(info['upload_date'])}\n"
    if info["duration"]:
        dur_min = info["duration"] // 60
        dur_sec = info["duration"] % 60
        md += f"duration: \"{dur_min}分{dur_sec}秒\"\n"
    md += f"subtitle_lang: \"{lang}\"\n"
    md += f"subtitle_type: \"{'自动生成' if is_auto else '手动上传'}\"\n"
    md += f"converted_at: \"{datetime.now().strftime('%Y-%m-%d %H:%M')}\"\n"
    md += "---\n\n"

    # ── 标题与元信息 ──
    md += f"# {title}\n\n"
    md += f"**频道：** {info['channel']}  \n"
    if info["upload_date"]:
        md += f"**上传日期：** {date_to_readable(info['upload_date'])}  \n"
    if info["duration"]:
        md += f"**时长：** {dur_min} 分 {dur_sec} 秒  \n"
    md += f"**字幕：** {lang}（{'自动生成' if is_auto else '手动上传'}）  \n"
    md += f"**来源：** [{info['url']}]({info['url']})\n\n"

    # ── 视频描述（如果有） ──
    if info["description"] and info["description"].strip():
        desc = info["description"].strip()
        # 限制描述长度，避免过长
        if len(desc) > 1500:
            desc = desc[:1500] + "\n\n...（描述过长，已截断）"
        md += "---\n\n"
        md += "## 📝 视频描述\n\n"
        md += desc + "\n\n"

    # ── 字幕正文 ──
    md += "---\n\n"
    md += "## 🎬 字幕内容\n\n"

    for i, para in enumerate(paragraphs):
        timestamp = seconds_to_timestamp(para["start"])
        md += f"> **[{timestamp}]** {para['text']}\n\n"

    # ── 脚注 ──
    md += "---\n\n"
    md += f"*本文由 `youtube_to_md.py` 自动生成，字幕来源 YouTube。*\n"
    md += f"*段落由 AI 规则自动合并，可能存在误差，建议对照原视频复核。*\n"

    return md, safe_title


# ── 主流程 ───────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="YouTube → Markdown 转换工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python youtube_to_md.py https://www.youtube.com/watch?v=xxxxx
  python youtube_to_md.py https://youtu.be/xxxxx
  python youtube_to_md.py --no-description https://www.youtube.com/watch?v=xxxxx
        """,
    )
    parser.add_argument("url", help="YouTube 视频 URL")
    parser.add_argument(
        "--no-description",
        action="store_true",
        help="不包含视频描述（精简输出）",
    )
    parser.add_argument(
        "--max-gap",
        type=float,
        default=MAX_GAP_SECONDS,
        help=f"段落合并的最大时间间隔（秒，默认 {MAX_GAP_SECONDS}）",
    )
    parser.add_argument(
        "-o", "--output-dir",
        default=OUTPUT_DIR,
        help=f"输出目录（默认当前目录）",
    )
    args = parser.parse_args()

    url = args.url.strip()

    # ── 第1步：获取视频信息 ──
    info = get_video_info(url)
    print(f"   ✅ 标题：{info['title']}")
    print(f"   ✅ 频道：{info['channel']}")
    if info["duration"]:
        print(f"   ✅ 时长：{info['duration'] // 60} 分 {info['duration'] % 60} 秒")

    # ── 第2步：选择合适的字幕语言 ──
    lang, is_auto = pick_subtitle_lang(url)

    if lang is None:
        print("\n❌ 该视频没有任何可用字幕。")
        print("   可能原因：")
        print("   1. 视频未开启字幕功能")
        print("   2. 视频语言不支持中英文")
        print("\n💡 建议：尝试其他有字幕的 YouTube 视频，或手动上传字幕后再试。")
        sys.exit(1)

    # ── 第3步：下载字幕 ──
    vtt_text = download_subtitle(url, lang, is_auto)

    # ── 第4步：解析并清理字幕 ──
    print("🔧 解析字幕...")
    segments = parse_vtt(vtt_text)
    print(f"   ✅ 提取 {len(segments)} 条字幕片段")

    # ── 第5步：合并为段落 ──
    print("📝 合并为段落...")
    paragraphs = merge_segments(segments, max_gap=args.max_gap)
    print(f"   ✅ 合并为 {len(paragraphs)} 个段落")

    # ── 第6步：生成 Markdown ──
    print("📄 生成 Markdown...")
    if args.no_description:
        info["description"] = ""
    md_content, safe_title = generate_markdown(info, paragraphs, lang, is_auto)

    # ── 第7步：保存文件 ──
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{safe_title}.md"

    # 如果文件已存在，加数字后缀
    if output_path.exists():
        counter = 1
        while (output_dir / f"{safe_title}_{counter}.md").exists():
            counter += 1
        output_path = output_dir / f"{safe_title}_{counter}.md"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"\n✅ 转换完成！")
    print(f"   📄 输出文件：{output_path}")
    print(f"   📊 字幕片段：{len(segments)} → {len(paragraphs)} 段落")
    print(f"   🌐 字幕语言：{lang}（{'自动生成' if is_auto else '手动上传'}）")


if __name__ == "__main__":
    main()
