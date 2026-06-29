"""
海外网红汉学传播 —— 评论区词云生成
目标：大山（Dashan）+ 歪果仁研究协会（YChina）
数据源：B站 API（bilibili-api-python，自带 WBI 签名）
输出：桌面两张词云 PNG

使用：python comment_wordcloud.py
"""

import os
import re
import sys
import time
import collections
from pathlib import Path

# ── 第三方库 ──
import jieba
import jieba.analyse
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use("Agg")  # 非交互后端
import matplotlib.pyplot as plt
from wordcloud import WordCloud, ImageColorGenerator

# B站 API
from bilibili_api import search, comment, video, user, sync

# ═══════════════════════════════════════════
# 全局配置
# ═══════════════════════════════════════════

OUTPUT_DIR = Path.home() / "Desktop"
FONT_PATH = "C:/Windows/Fonts/simhei.ttf"  # 黑体，确保中文显示
MASK_IMAGE = None  # 可选：用圆形/云朵 mask
MAX_COMMENTS = 500  # 每个频道最多拉取评论数
COMMENTS_PER_VIDEO = 100  # 每个视频最多拉取评论数
TOP_VIDEOS = 5  # 每个频道取前 N 个视频

# 中文停用词（高频无意义词 + B站弹幕/评论专用）
STOPWORDS = set([
    # 通用停用词
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一",
    "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着",
    "没有", "看", "好", "自己", "这", "他", "她", "它", "们", "那", "些",
    "所", "为", "所以", "因为", "但是", "可以", "这个", "那个", "还", "让",
    "被", "把", "从", "与", "及", "或", "但", "而", "且", "虽然", "如果",
    "什么", "怎么", "哪", "吗", "啊", "吧", "呢", "哦", "嗯", "哈", "呀",
    "真的", "觉得", "然后", "就是", "那种", "应该", "已经", "比较", "其实",
    "不太", "有点", "不能", "之后", "这么", "那么", "这样", "那样",
    "对", "能", "想", "做", "会", "知道", "没", "去", "来", "过",
    # B站/评论专用
    "哈哈哈", "哈哈哈哈", "哈哈", "233", "2333", "弹幕", "打卡", "来了",
    "前排", "第一", "有人", "有没有", "up", "up主", "视频", "这个视频",
    "大家", "各位", "小伙伴", "朋友", "谢谢", "感谢", "加油",
    "1", "2", "3", "4", "5", "6", "7", "8", "9", "0",
    "bilibili", "哔哩哔哩", "b站", "BV", "av",
    # 英文通用
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "can", "shall", "to", "of", "in", "for",
    "on", "with", "at", "by", "from", "as", "into", "through", "during",
    "it", "its", "this", "that", "these", "those", "i", "you", "he", "she",
    "they", "we", "me", "him", "her", "us", "them", "my", "your", "his",
    "and", "but", "or", "not", "no", "so", "if", "then", "than", "too",
    "very", "just", "about", "also", "only", "all", "some", "any", "each",
])

# jieba 自定义词典（人名、专有名词等）
CUSTOM_WORDS = [
    "歪果仁", "歪研会", "高佑思", "方晔顿", "刘祺", "星悦",
    "大山", "大山读诗词", "朗诵", "相声", "古诗词",
    "中国文化", "中国诗词", "静夜思", "将进酒", "满江红", "水调歌头",
    "李白", "苏轼", "杜甫", "岳飞", "唐诗", "宋词", "楚辞",
    "美美与共", "央视", "春晚", "加拿大", "外国人", "老外",
    "跨文化", "文化差异", "中国话", "中文", "汉语",
    "别见外", "中国城市计划", "街头采访", "新疆棉花",
    "传统文化", "书法", "汉字", "诗词", "诗歌",
    "中华文化", "汉学", "中西文化", "文化传播", "文化融合",
    "太好听了", "太美了", "泪目", "破防", "自豪", "骄傲",
    "感动", "震撼", "惊艳", "令人惊叹", "不可思议",
]
for w in CUSTOM_WORDS:
    jieba.add_word(w)


# ═══════════════════════════════════════════
# 数据获取
# ═══════════════════════════════════════════

def clean_text(text: str) -> str:
    """清洗评论文本"""
    # 去除 emoji 和特殊符号
    text = re.sub(r'\[.*?\]', '', text)  # [表情] 类弹幕标记
    text = re.sub(r'[^一-鿿㐀-䶿a-zA-Z　-〿＀-￯]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def get_bilibili_uid_by_name(name: str) -> int:
    """通过用户名搜索 B站 UID"""
    print(f"  🔍 搜索用户: {name}")
    try:
        result = sync(search.search_by_type(name, search_type=search.SearchObjectType.USER))
        if result and result.get("result"):
            for u in result["result"][:3]:
                uname = u.get("uname", "")
                if name.lower() in uname.lower() or len(result["result"]) == 1:
                    mid = u["mid"]
                    print(f"  ✅ 找到: {uname} (UID: {mid})")
                    return mid
        # 返回第一个结果
        if result and result.get("result"):
            return result["result"][0]["mid"]
    except Exception as e:
        print(f"  ⚠️ 搜索失败: {e}")
    return None


def fetch_video_comments(avid: int, max_count: int = 100) -> list[str]:
    """获取单个视频的评论"""
    comments = []
    page = 1
    while len(comments) < max_count and page <= 10:
        try:
            result = sync(comment.get_comments(
                oid=avid,
                type_=comment.CommentResourceType.VIDEO,
                page_index=page,
                order=comment.OrderType.LIKE,
            ))
            if result and result.get("replies"):
                for reply in result["replies"]:
                    msg = reply.get("content", {}).get("message", "")
                    msg = clean_text(msg)
                    if msg and len(msg) >= 2:  # 至少两个字
                        comments.append(msg)
                page += 1
                time.sleep(0.5)  # 礼貌间隔
            else:
                break
        except Exception as e:
            print(f"    ⚠️ 评论获取失败 (page={page}): {e}")
            break
    return comments[:max_count]


def fetch_channel_comments(uid: int, label: str) -> list[str]:
    """获取频道热门视频的评论"""
    all_comments = []
    print(f"\n📺 [{label}] 获取视频列表 (UID: {uid})")

    try:
        # 获取用户投稿视频
        user_obj = user.User(uid)
        videos_data = sync(user_obj.get_videos(ps=TOP_VIDEOS))
    except Exception as e:
        print(f"  ❌ 获取视频列表失败: {e}")
        return all_comments

    if not videos_data or not videos_data.get("list", {}).get("vlist"):
        print(f"  ❌ 未找到视频")
        return all_comments

    vlist = videos_data["list"]["vlist"][:TOP_VIDEOS]
    print(f"  📋 找到 {len(vlist)} 个视频")

    for vi, v in enumerate(vlist):
        avid = v["aid"]
        title = v.get("title", "N/A")
        play = v.get("play", "?")
        print(f"  [{vi+1}/{len(vlist)}] {title[:50]}... (播放:{play})")

        comments = fetch_video_comments(avid, max_count=COMMENTS_PER_VIDEO)
        print(f"    💬 获取 {len(comments)} 条评论")
        all_comments.extend(comments)

        if len(all_comments) >= MAX_COMMENTS:
            break

    return all_comments[:MAX_COMMENTS]


# ═══════════════════════════════════════════
# 词云生成
# ═══════════════════════════════════════════

def segment_texts(comments: list[str]) -> str:
    """中文分词 + 去停用词，返回空格分隔的词串"""
    words = []
    for text in comments:
        seg_list = jieba.cut(text, cut_all=False)
        for w in seg_list:
            w = w.strip().lower()
            if len(w) >= 2 and w not in STOPWORDS:
                words.append(w)
    return " ".join(words)


def generate_wordcloud(word_text: str, title: str, output_name: str, mask_path: str = None):
    """生成词云图并保存"""
    print(f"\n🎨 生成词云: {title}")

    # 加载 mask（可选）
    mask = None
    if mask_path and os.path.exists(mask_path):
        mask = np.array(Image.open(mask_path))

    # 创建词云
    wc = WordCloud(
        font_path=FONT_PATH,
        mask=mask,
        background_color="white",
        max_words=200,
        max_font_size=120,
        min_font_size=8,
        width=1200,
        height=800,
        margin=10,
        collocations=False,  # 不合并词组
        prefer_horizontal=0.7,
        random_state=42,
        colormap="viridis",
        scale=2,  # 高清输出
    )

    wc.generate(word_text)

    # 绘图
    fig, ax = plt.subplots(figsize=(14, 10), dpi=150)
    ax.imshow(wc, interpolation="bilinear")
    ax.set_title(title, fontsize=22, fontproperties="SimHei", pad=20)
    ax.axis("off")

    output_path = OUTPUT_DIR / output_name
    fig.savefig(str(output_path), dpi=150, bbox_inches="tight", facecolor="white", edgecolor="none")
    plt.close(fig)

    # 统计
    word_freq = wc.words_
    top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:15]

    print(f"  ✅ 已保存: {output_path}")
    print(f"  📊 TOP 15 高频词:")
    for i, (w, freq) in enumerate(top_words, 1):
        bar = "█" * int(freq * 200)
        print(f"  {i:2d}. {w:<10s} {bar}")
    print()

    return top_words


# ═══════════════════════════════════════════
# 主流程
# ═══════════════════════════════════════════

def main():
    print("=" * 60)
    print("  海外网红汉学传播 — 评论区词云生成")
    print("=" * 60)

    # ── 案例一：大山 ──
    print("\n" + "=" * 60)
    print("  案例一：大山 (Dashan)")
    print("=" * 60)

    dashan_uid = get_bilibili_uid_by_name("大山")
    dashan_comments = []
    if dashan_uid:
        dashan_comments = fetch_channel_comments(dashan_uid, "大山")
    else:
        print("  ❌ 无法找到大山 B站账号，尝试手动指定 UID...")
        # 尝试已知 UID（可能需要手动查找）
        # 备用：直接搜索"大山读诗词"等关键词的视频评论

    if len(dashan_comments) < 20:
        print("\n  ⚠️ B站评论获取不足，尝试通过关键词搜索视频评论...")
        try:
            # 搜索大山相关视频并获取评论
            search_result = sync(search.search_by_type(
                "大山 诗词 朗诵", search_type=search.SearchObjectType.VIDEO
            ))
            if search_result and search_result.get("result"):
                extra = []
                for v in search_result["result"][:TOP_VIDEOS]:
                    avid = v.get("aid") or v.get("id", 0)
                    if avid:
                        c = fetch_video_comments(int(avid), max_count=50)
                        extra.extend(c)
                        time.sleep(0.5)
                print(f"  📋 通过搜索获取额外 {len(extra)} 条评论")
                dashan_comments.extend(extra)
        except Exception as e:
            print(f"  ⚠️ 搜索备选方案也失败: {e}")

    print(f"\n  📊 大山 总计获取: {len(dashan_comments)} 条评论")

    # ── 案例二：歪果仁研究协会 ──
    print("\n" + "=" * 60)
    print("  案例二：歪果仁研究协会 (YChina)")
    print("=" * 60)

    yc_uid = 32820037  # 已知 UID
    print(f"  🔍 使用已知 UID: {yc_uid}")
    yc_comments = fetch_channel_comments(yc_uid, "歪果仁研究协会")

    print(f"\n  📊 歪果仁研究协会 总计获取: {len(yc_comments)} 条评论")

    # ── 分词 ──
    print("\n" + "=" * 60)
    print("  🔪 中文分词 & 停用词过滤")
    print("=" * 60)

    dashan_text = segment_texts(dashan_comments) if dashan_comments else ""
    yc_text = segment_texts(yc_comments) if yc_comments else ""

    if not dashan_text and not yc_text:
        print("\n❌ 两个频道都没获取到评论，无法生成词云。")
        print("可能原因：B站 API 限流、网络问题、或频道无评论。")
        sys.exit(1)

    print(f"  大山: {len(dashan_comments)} 条评论 → {len(dashan_text.split())} 个有效词")
    print(f"  歪果仁研究协会: {len(yc_comments)} 条评论 → {len(yc_text.split())} 个有效词")

    # ── 生成词云 ──
    print("\n" + "=" * 60)
    print("  ☁️  生成词云图")
    print("=" * 60)

    results = {}

    if dashan_text:
        results["dashan"] = generate_wordcloud(
            dashan_text,
            title="大山（Dashan）— 评论区词云",
            output_name="词云_大山_Dashan.png",
        )

        # 额外生成一张词频柱状图
        if results["dashan"]:
            top15 = results["dashan"]
            fig, ax = plt.subplots(figsize=(14, 8))
            words, freqs = zip(*top15[::-1])  # 反转（低频在上）
            ax.barh(range(len(words)), freqs, color=plt.cm.viridis(np.linspace(0.2, 0.8, len(words))))
            ax.set_yticks(range(len(words)))
            ax.set_yticklabels(words, fontproperties="SimHei", fontsize=12)
            ax.set_xlabel("词频", fontsize=12)
            ax.set_title("大山（Dashan）评论区 — TOP 15 高频词", fontsize=16, fontproperties="SimHei")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            bar_path = OUTPUT_DIR / "词云_大山_Dashan_柱状图.png"
            fig.savefig(str(bar_path), dpi=150, bbox_inches="tight", facecolor="white")
            plt.close(fig)
            print(f"  📊 柱状图: {bar_path}")

    if yc_text:
        results["yca"] = generate_wordcloud(
            yc_text,
            title="歪果仁研究协会（YChina）— 评论区词云",
            output_name="词云_歪果仁研究协会_YChina.png",
        )

        if results["yca"]:
            top15 = results["yca"]
            fig, ax = plt.subplots(figsize=(14, 8))
            words, freqs = zip(*top15[::-1])
            ax.barh(range(len(words)), freqs, color=plt.cm.plasma(np.linspace(0.2, 0.8, len(words))))
            ax.set_yticks(range(len(words)))
            ax.set_yticklabels(words, fontproperties="SimHei", fontsize=12)
            ax.set_xlabel("词频", fontsize=12)
            ax.set_title("歪果仁研究协会（YChina）评论区 — TOP 15 高频词", fontsize=16, fontproperties="SimHei")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            bar_path = OUTPUT_DIR / "词云_歪果仁研究协会_YChina_柱状图.png"
            fig.savefig(str(bar_path), dpi=150, bbox_inches="tight", facecolor="white")
            plt.close(fig)
            print(f"  📊 柱状图: {bar_path}")

    # ── 收尾 ──
    print("\n" + "=" * 60)
    print("  ✅ 全部完成！")
    print(f"  输出目录: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
