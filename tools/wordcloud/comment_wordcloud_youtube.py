"""
海外网红汉学传播 —— 评论区词云生成 (YouTube 路线)
数据源：YouTube（scrapetube + youtube-comment-downloader）
输出：桌面词云 PNG + 柱状图
"""

import os, re, sys, time, collections
from pathlib import Path

import jieba
import jieba.analyse
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from wordcloud import WordCloud

import scrapetube
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR

# ═══════════════════════════════════
# 配置
# ═══════════════════════════════════
OUTPUT_DIR = Path.home() / "Desktop"
FONT_PATH = "C:/Windows/Fonts/simhei.ttf"
MAX_VIDEOS = 8       # 每个频道最多取几个视频
MAX_COMMENTS = 100    # 每个视频最多取多少条
TOTAL_TARGET = 400    # 每个频道目标评论总数

# 中文停用词
STOPWORDS = set([
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一",
    "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着",
    "没有", "看", "好", "自己", "这", "他", "她", "它", "们", "那", "些",
    "所", "为", "所以", "因为", "但是", "可以", "这个", "那个", "还", "让",
    "被", "把", "从", "与", "及", "或", "但", "而", "且", "虽然", "如果",
    "什么", "怎么", "哪", "吗", "啊", "吧", "呢", "哦", "嗯", "哈", "呀",
    "真的", "觉得", "然后", "就是", "那种", "应该", "已经", "比较", "其实",
    "不太", "有点", "不能", "之后", "这么", "那么", "这样", "那样",
    "对", "能", "想", "做", "知道", "没", "来", "过",
    "哈哈哈", "哈哈哈哈", "哈哈", "弹幕", "打卡", "来了",
    "前排", "第一", "有人", "有没有", "大家", "各位",
    "bilibili", "哔哩哔哩",
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "can", "shall", "to", "of", "in", "for",
    "on", "with", "at", "by", "from", "as", "into", "through", "during",
    "it", "its", "this", "that", "these", "those", "i", "you", "he", "she",
    "they", "we", "me", "him", "her", "us", "them", "my", "your", "his",
    "and", "but", "or", "not", "no", "so", "if", "then", "than", "too",
    "very", "just", "about", "also", "only", "all", "some", "any", "each",
    "1", "2", "3", "4", "5",
])

# 自定义词典
CUSTOM_WORDS = [
    "歪果仁", "歪研会", "高佑思", "大山", "朗诵", "相声", "古诗词",
    "中国文化", "中国诗词", "静夜思", "将进酒", "满江红", "水调歌头",
    "李白", "苏轼", "杜甫", "岳飞", "唐诗", "宋词", "楚辞",
    "美美与共", "央视", "春晚", "加拿大", "外国人", "老外",
    "跨文化", "文化差异", "中国话", "中文", "汉语",
    "别见外", "传统文化", "书法", "汉字", "诗词", "诗歌",
    "中华文化", "汉学", "中西文化", "文化传播", "文化融合",
    "太好听了", "太美了", "泪目", "破防", "自豪", "骄傲",
    "感动", "震撼", "惊艳", "令人惊叹", "不可思议",
]
for w in CUSTOM_WORDS:
    jieba.add_word(w)

# ═══════════════════════════════════
# 评论抓取
# ═══════════════════════════════════

def clean_text(text: str) -> str:
    """清洗文本：去表情标记、特殊字符、保留中英文"""
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'[^一-鿿㐀-䶿a-zA-Z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def get_channel_videos(channel_url: str, max_videos: int = MAX_VIDEOS) -> list:
    """通过 scrapetube 获取频道视频 ID 列表"""
    video_ids = []
    print(f"  Fetching videos from: {channel_url}")
    try:
        videos = scrapetube.get_channel(channel_url=channel_url, limit=max_videos)
        for v in videos:
            vid = v.get("videoId", "")
            if vid:
                video_ids.append(vid)
        print(f"  Found {len(video_ids)} video IDs")
    except Exception as e:
        print(f"  ERROR: {e}")
    return video_ids


def search_videos(keyword: str, max_videos: int = MAX_VIDEOS) -> list:
    """通过 scrapetube 搜索视频并返回 ID 列表"""
    video_ids = []
    print(f"  Searching for: {keyword}")
    try:
        videos = scrapetube.get_search(keyword, limit=max_videos)
        for v in videos:
            vid = v.get("videoId", "")
            if vid:
                video_ids.append(vid)
        print(f"  Found {len(video_ids)} video IDs")
    except Exception as e:
        print(f"  ERROR: {e}")
    return video_ids


def fetch_comments_from_videos(video_ids: list, max_per_video: int = MAX_COMMENTS) -> list:
    """从视频列表获取评论"""
    downloader = YoutubeCommentDownloader()
    all_comments = []

    for i, vid in enumerate(video_ids):
        if len(all_comments) >= TOTAL_TARGET:
            break
        print(f"  [{i+1}/{len(video_ids)}] Video: {vid}")
        try:
            comments_gen = downloader.get_comments_from_url(
                f"https://www.youtube.com/watch?v={vid}",
                sort_by=SORT_BY_POPULAR
            )
            count = 0
            for c in comments_gen:
                text = clean_text(c.get("text", ""))
                if text and len(text) >= 2:
                    all_comments.append(text)
                    count += 1
                    if count >= max_per_video:
                        break
            print(f"    Got {count} comments")
            time.sleep(1.0)  # rate limit protection
        except Exception as e:
            print(f"    Error: {e}")
            time.sleep(2.0)

    return all_comments


# ═══════════════════════════════════
# 分词
# ═══════════════════════════════════

def segment_texts(comments: list) -> str:
    """中文分词 + 去停用词"""
    words = []
    for text in comments:
        for w in jieba.cut(text, cut_all=False):
            w = w.strip().lower()
            if len(w) >= 2 and w not in STOPWORDS:
                words.append(w)
    return " ".join(words)


# ═══════════════════════════════════
# 词云生成
# ═══════════════════════════════════

def generate_wordcloud(word_text: str, title: str, output_name: str):
    """生成词云图并保存"""
    print(f"\n  Generating word cloud: {title}")

    wc = WordCloud(
        font_path=FONT_PATH,
        background_color="white",
        max_words=200,
        max_font_size=120,
        min_font_size=8,
        width=1200,
        height=800,
        margin=10,
        collocations=False,
        prefer_horizontal=0.7,
        random_state=42,
        colormap="viridis",
        scale=2,
    )
    wc.generate(word_text)

    fig, ax = plt.subplots(figsize=(14, 10), dpi=150)
    ax.imshow(wc, interpolation="bilinear")
    ax.set_title(title, fontsize=22, fontproperties="SimHei", pad=20)
    ax.axis("off")

    output_path = OUTPUT_DIR / output_name
    fig.savefig(str(output_path), dpi=150, bbox_inches="tight", facecolor="white", edgecolor="none")
    plt.close(fig)

    # top 15
    top_words = sorted(wc.words_.items(), key=lambda x: x[1], reverse=True)[:15]
    print(f"  Saved: {output_path}")
    print(f"  TOP 15 words:")
    for i, (w, freq) in enumerate(top_words, 1):
        bar = "#" * int(freq * 200)
        print(f"  {i:2d}. {w:<12s} {bar}")

    return top_words


def generate_bar_chart(top_words: list, title: str, output_name: str):
    """生成词频柱状图"""
    fig, ax = plt.subplots(figsize=(14, 8))
    words, freqs = zip(*top_words[::-1])
    ax.barh(range(len(words)), freqs, color=plt.cm.viridis(np.linspace(0.2, 0.8, len(words))))
    ax.set_yticks(range(len(words)))
    ax.set_yticklabels(words, fontproperties="SimHei", fontsize=12)
    ax.set_xlabel("Word Frequency", fontsize=12)
    ax.set_title(title, fontsize=16, fontproperties="SimHei")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    output_path = OUTPUT_DIR / output_name
    fig.savefig(str(output_path), dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  Bar chart saved: {output_path}")


# ═══════════════════════════════════
# 主流程
# ═══════════════════════════════════

def main():
    print("=" * 60)
    print("  Word Cloud - YouTube Comments (Dashan & YChina)")
    print("=" * 60)

    # ── Case 1: Dashan ──
    print("\n" + "=" * 60)
    print("  [1/2] Dashan (DashanTV)")
    print("=" * 60)

    # Try channel URL first, then search
    dashan_ids = get_channel_videos("https://www.youtube.com/@DashanTV")
    if len(dashan_ids) < 3:
        print("  Channel videos insufficient, trying search...")
        extra = search_videos("Dashan Chinese poetry recitation")
        dashan_ids.extend(extra)
        dashan_ids = list(dict.fromkeys(dashan_ids))  # dedupe

    print(f"\n  Total Dashan video IDs: {len(dashan_ids)}")
    dashan_comments = fetch_comments_from_videos(dashan_ids) if dashan_ids else []
    print(f"\n  Total Dashan comments: {len(dashan_comments)}")

    # ── Case 2: YChina ──
    print("\n" + "=" * 60)
    print("  [2/2] YChina (歪果仁研究协会)")
    print("=" * 60)

    yc_ids = get_channel_videos("https://www.youtube.com/@YChina")
    if len(yc_ids) < 3:
        print("  Channel videos insufficient, trying search...")
        extra = search_videos("歪果仁研究协会 Chinese culture")
        yc_ids.extend(extra)
        yc_ids = list(dict.fromkeys(yc_ids))

    print(f"\n  Total YChina video IDs: {len(yc_ids)}")
    yc_comments = fetch_comments_from_videos(yc_ids) if yc_ids else []
    print(f"\n  Total YChina comments: {len(yc_comments)}")

    # ── Segmentation ──
    print("\n" + "=" * 60)
    print("  Chinese Word Segmentation (jieba)")
    print("=" * 60)

    dashan_text = segment_texts(dashan_comments) if dashan_comments else ""
    yc_text = segment_texts(yc_comments) if yc_comments else ""

    print(f"  Dashan: {len(dashan_comments)} comments -> {len(dashan_text.split())} words")
    print(f"  YChina: {len(yc_comments)} comments -> {len(yc_text.split())} words")

    if not dashan_text and not yc_text:
        print("\n  ERROR: No comments retrieved from either channel.")
        print("  Possible reasons: YouTube rate limiting, network issues.")
        return

    # ── Word Clouds ──
    print("\n" + "=" * 60)
    print("  Generating Word Clouds")
    print("=" * 60)

    if dashan_text and len(dashan_text.split()) > 20:
        top = generate_wordcloud(
            dashan_text,
            "Dashan - Audience Comment Word Cloud",
            "wordcloud_Dashan.png"
        )
        if top:
            generate_bar_chart(top, "Dashan - Top 15 Keywords", "wordcloud_Dashan_bar.png")
    else:
        print("\n  Dashan: insufficient data for word cloud")

    if yc_text and len(yc_text.split()) > 20:
        top = generate_wordcloud(
            yc_text,
            "YChina - Audience Comment Word Cloud",
            "wordcloud_YChina.png"
        )
        if top:
            generate_bar_chart(top, "YChina - Top 15 Keywords", "wordcloud_YChina_bar.png")
    else:
        print("\n  YChina: insufficient data for word cloud")

    print("\n" + "=" * 60)
    print(f"  Done! Output: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
