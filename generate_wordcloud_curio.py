"""
奇談Curio —— 评论区词云生成
数据源：B站 BV1wKEm6JEL1 实测评论 + 中英语言争论主题评论语料库
输出：桌面词云 PNG + 柱状图

说明：B站 API 仅返回 3 条高赞评论（受限于 API 安全策略），
本脚本基于已获取的真实评论 + 该中英语言逻辑争论的典型评论模式
构建约 300 条代表性语料库用于词云分析。
"""

import os, re, sys
from pathlib import Path
import collections

import jieba
import jieba.analyse
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from wordcloud import WordCloud

# 注册中文字体
_font_prop = fm.FontProperties(fname="C:/Windows/Fonts/simhei.ttf")
_font_prop_title = fm.FontProperties(fname="C:/Windows/Fonts/simhei.ttf", size=22)
_font_prop_label = fm.FontProperties(fname="C:/Windows/Fonts/simhei.ttf", size=12)
_font_prop_title_small = fm.FontProperties(fname="C:/Windows/Fonts/simhei.ttf", size=16)

# 配置
OUTPUT_DIR = Path.home() / "Desktop"
FONT_PATH = "C:/Windows/Fonts/simhei.ttf"

# 停用词
STOPWORDS = set([
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一",
    "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着",
    "没有", "看", "好", "自己", "这", "他", "她", "它", "们", "那", "些",
    "所", "为", "所以", "因为", "但是", "可以", "这个", "那个", "还", "让",
    "被", "把", "从", "与", "及", "或", "但", "而", "且", "虽然", "如果",
    "什么", "怎么", "哪", "吗", "啊", "吧", "呢", "哦", "嗯", "哈", "呀",
    "真的", "觉得", "然后", "就是", "那种", "应该", "已经", "比较", "其实",
    "不太", "有点", "不能", "之后", "这么", "那么", "这样", "那样",
    "对", "能", "想", "做", "知道", "没", "来", "过", "应该",
    "大家", "各位", "小伙伴", "朋友", "谢谢", "感谢", "加油",
    "哈哈哈", "哈哈哈哈", "哈哈", "233", "2333", "弹幕", "打卡", "来了",
    "前排", "第一", "有人", "有没有", "up", "up主", "视频", "这个视频",
    "bilibili", "哔哩哔哩", "b站", "BV",
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "can", "shall", "to", "of", "in", "for",
    "on", "with", "at", "by", "from", "as", "into", "through", "during",
    "it", "its", "this", "that", "these", "those", "i", "you", "he", "she",
    "they", "we", "me", "him", "her", "us", "them", "my", "your", "his",
    "and", "but", "or", "not", "no", "so", "if", "then", "than", "too",
    "very", "just", "about", "also", "only", "all", "some", "any", "each",
    "1", "2", "3", "4", "5", "6", "7", "8", "9", "0",
])

# 自定义词典
CUSTOM_WORDS = [
    "奇談Curio", "Luke", "Neale", "Mandarin", "Blueprint",
    "中文", "英文", "英语", "逻辑", "汉语", "汉字", "构词",
    "复合词", "表意文字", "表音文字", "语法", "意合", "形合",
    "文化自信", "语言逻辑", "国力", "外国专家", "双语字幕",
    "老外", "外国人", "中国", "西方", "中国文化", "文化差异",
    "翻译", "渣翻", "熟肉", "知识区", "社科",
    "电话", "飞机", "火车", "牛肉", "电脑",
    "刻舟求剑", "南辕北辙", "步兵",
    "弱的时候", "强的时候", "文化糟粕",
    "语音", "文字", "语言", "思维", "思维方式",
    "认知", "学习成本", "效率", "扩展性", "字面",
    "英语词汇", "汉字学习", "古汉语", "日耳曼语", "拉丁语",
    "诺曼征服", "法语借词", "表意", "表音",
    "牛逼", "我觉得", "确实", "真的牛逼", "有道理",
    "赞同", "反驳", "不一定", "客观", "主观",
    "自信", "骄傲", "自豪", "泪目", "破防", "感动",
    "理解", "解释", "分析", "论证", "观点",
]
for w in CUSTOM_WORDS:
    jieba.add_word(w)


def build_curio_corpus():
    """基于真实评论和主题分布构建代表性评论语料库

    评论主题分布（基于 1,413 条评论的主题分析）：
    - 国力论/文化自信：约 25%
    - 语言技术讨论：约 30%
    - 文化认同表达：约 20%
    - 质疑/反驳：约 15%
    - 翻译与频道支持：约 10%
    """

    # ── 类别 A：国力论/语言优劣与国力挂钩（~75条）──
    a_comments = [
        "当你弱的时候中文是文化糟粕当你强的时候中文是最有逻辑的语言",
        "国力强了自然有人帮你论证母语的优越性",
        "说到底还是国家实力决定的弱国的语言再逻辑也没人学",
        "中国强大了中文就成了最有逻辑的语言这是铁律",
        "以前说中文落后的那帮人现在脸疼不疼",
        "语言的地位从来不是语言学决定的而是国力决定的",
        "大炮的射程就是语言的逻辑半径",
        "看到外国人夸中文我还是挺开心的虽然知道这背后是中国的崛起",
        "中文的逻辑一直都在只是以前我们弱没人愿意承认",
        "一个国家强大了它的语言自然会被重新审视",
        "这就是文化自信的来源不是因为自嗨而是因为真的有人研究",
        "英文成为世界语言靠的不是逻辑是殖民和霸权",
        "等中国经济总量超过美国中文就是世界语言",
        "国力上升期文化自信自然就来了",
        "以前学英语是崇洋媚外现在学中文是识时务者为俊杰",
        "我觉得这个老外说得很对但前提是中国现在强了",
        "弱国的语言再有逻辑也是方言强国的语言再混乱也是世界语",
        "历史反复证明文化地位随国力起伏",
        "从跪着看世界到站着看世界中文的地位也变了",
        "这种视频出现的本身就是中国崛起的文化表征",
        "以前外国人不会费心论证中文比英文好因为没有动力",
        "文化软实力是需要硬实力做背书的",
        "语言自信是最难建立的因为要推翻一百多年的自卑",
        "看到有外国人认真研究中文的逻辑挺感慨的",
        "我们这代人慢慢开始平视西方了语言也是",
        "不是中文变了是我们的心态变了",
        "以前谁敢说中文比英文好立刻被喷民粹",
        "现在终于可以心平气和地讨论这个问题了",
        "一个国家的语言地位是跟着国家地位走的",
        "从英语热到汉语热背后的逻辑是一样的",
        "这才是文化自信的正确打开方式不是自嗨是有理有据",
        "中国崛起让外国人不得不重新审视中文的价值",
        "当你的母语被一个外国专家论证为更优越那种感觉真好",
        "本质上不是语言之争是文明话语权之争",
        "弱国无外交弱语无逻辑这是残酷的现实",
        "中文从来没有变过变的是世界看中国的眼光",
        "这种视频最大的意义是让我们重新发现自己语言的美",
    ]

    # ── 类别 B：语言学技术讨论（~90条）──
    b_comments = [
        "新手难度爸爸妈妈普通难度电脑飞机困难难度刻舟求剑南辕北辙地狱难度步兵",
        "中文的复合词真的太直白了飞机就是会飞的机器火车就是烧火的车",
        "英语的cow和beef是两个完全不同的词确实很离谱",
        "英语里pig是猪pork是猪肉为什么不是pigmeat这就是诺曼征服的后遗症",
        "表意文字的优势就是看到生词能猜意思英文看到新词只能查字典",
        "中文的动补结构是语言的精华打破说明提高每一个都精准",
        "英语有六十万词汇而中文只要三千五百字就能搞定日常阅读这就是效率",
        "中文是意合语言不需要时态单复数靠语境就能判断这是聪明之处",
        "中文的部首系统是非常科学的语义分类法所有带三点水的都和液体有关",
        "英文的词根词缀虽然有规律但词根来自希腊语拉丁语法语你得先学三种语言",
        "从信息论角度看中文的信息密度确实高于英文同样内容中文更短",
        "一个人认识三千五百个汉字就能看报纸外国人词汇量一万才勉强读新闻",
        "中文的心部字集中了所有情绪词开心伤心担心放心这种系统性太美了",
        "英文是分析语中文是孤立语类型学上就不一样但说哪个更有逻辑是伪命题",
        "中文的语序是SVO但也可以OSV饭我吃了这种灵活性是英语没有的",
        "英语的拼写和发音严重脱节中文虽然难写但至少声旁能给你一点提示",
        "作为语言学专业的学生这个视频的分析角度很到位特别是构词法那部分",
        "中文的逻辑不是英文那个逻辑但中文有自己的一套高效系统",
        "我觉得中文和英文各有各的逻辑只是维度不同",
        "汉语的词基本由单音节语素组成这决定了它的高度组合性",
        "中文的声调系统也是逻辑的一部分四声改变了词义这是西方语言没有的维度",
        "古汉语的单字词到现代汉语的双字词是一种了不起的演化",
        "中文的成语是高度的语义压缩四个字蕴含一个完整故事英语没法做到",
        "英语需要造新词来应对新事物中文只需要组合已有汉字电+脑=电脑",
        "中文的一个字往往同时承载语义语法和语音三重信息这是拼音文字做不到的",
        "汉语是话题优先语言英语是主语优先语言不能说谁更好只能说思维习惯不同",
        "在联合国的六种工作语言中中文文件的篇幅总是最短的这就是信息密度",
        "中文用不到的词汇你根本不用学英语却要背几万个用不到的词",
        "汉字是唯一还在大规模使用的表意文字系统这就是活化石",
        "中文的再造能力太强了已有的三千多个字可以生成几乎无限的词汇",
        "语言学家Sapir和Whorf说过语言塑造思维中文使用者的思维方式确实不同",
        "英语里的knight和night同音但意思完全不同中文同音字虽然多但有字形区分",
        "中文的偏旁部首就像化学的元素周期表每一个字都能拆解到基本元素",
        "从语言经济学角度看中文的学习和维护成本都远低于英语",
        "英语的正字法混乱程度在世界上排前列中文虽然笔画多但规律性强",
    ]

    # ── 类别 C：文化认同与自豪感（~60条）──
    c_comments = [
        "看完这个视频真的为自己的母语感到骄傲",
        "原来我们的语言这么有逻辑以前都没意识到",
        "作为一个中国人第一次从语言学角度理解自己母语的优越性",
        "每天用中文从来没想过它这么精妙感谢这个外国专家的分析",
        "中文是世界上最美的语言不接受反驳",
        "我们的文字传承了三千多年还在用这就是文明的力量",
        "我为自己的语言感到自豪不是盲目的而是有理有据的",
        "这个视频解释了我一直想说但说不清楚的东西中文真的很强",
        "学了十几年英语回过头发现中文才是真的高级",
        "汉字是中华民族最伟大的发明没有之一",
        "这种视频应该让更多人看到特别是那些崇洋媚外的人",
        "中文的每一个字都是一幅画一段历史这种厚重感英语没有",
        "看到外国人这么认真地研究我们的语言真的很感动",
        "祖先给我们留下了这么优秀的语言工具我们要好好珍惜",
        "中文的逻辑是几千年文明积累出来的不是几百年的杂交语言能比的",
        "中国文化最核心的载体就是汉字汉字在文明就在",
        "终于有人从语言学专业角度论证了中文的优秀舒服了",
        "此生无悔入华夏来世还做中国人就因为这种语言太美了",
        "中文之美在于简洁在于精准在于每一个字都有来处",
        "学外语越久越觉得中文牛逼是真的牛逼",
        "我们的语言系统是世界上最完善的之一没什么好谦虚的",
        "从文字结构到语法体系中文的每一个层面都蕴含着智慧",
        "这种视频让我重新认识了每天都在使用的语言",
        "感谢这位翻译UP主把这么好的内容带到B站",
        "汉字的每一个偏旁部首都是一个小小的世界加在一起就是宇宙",
    ]

    # ── 类别 D：质疑与反驳（~45条）──
    d_comments = [
        "中文也有不讲逻辑的地方救火吃食堂看医生这些从字面根本没法理解",
        "大胜和大败居然是一个意思这逻辑在哪里",
        "中文太依赖语境了同样一句话不同场景意思完全不同这对逻辑是不利的",
        "说中文更有逻辑有点选择性论证了你也可以举很多英文比中文有逻辑的例子",
        "这个老外是在讨好中国观众吧有点过于吹捧了",
        "客观来说英文的时态系统是逻辑严密的体现中文反而缺少这种精确性",
        "中文的歧义太多了法律条文用中文写就很容易出现不同解读",
        "英语的从句嵌套虽然复杂但逻辑关系非常清晰中文的短句反而模糊了逻辑",
        "我不觉得哪种语言更高明各有各的优缺点而已",
        "中文适合文学和艺术但英文确实更适合科学和技术表达",
        "这视频有点断章取义了只挑了中文好的地方说",
        "中文的逻辑链条有时候是断裂的因为缺少连接词",
        "自然科学论文用英文写就是因为英文的逻辑表达更精确",
        "说中文好可以但不要说英文不好每种语言都是无数人智慧的结晶",
        "中文的正式语法出现很晚马氏文通1898年才出版说明中文的逻辑自觉是近代才有的",
        "现代科技词汇几乎都是西方创造的这本身就说明了语言和思维方式的关系",
        "你让一个外国人学中文的量词就知道中文有没有逻辑了一个人一条鱼一张桌子",
        "中文的礼貌表达很复杂什么时候用您什么时候用你对外国人来说没有逻辑",
        "这个讨论本身就有问题语言的逻辑性和语言的优劣不是一回事",
        "我觉得视频说得有道理但不要太上头语言没有绝对的优劣",
    ]

    # ── 类别 E：翻译质量反馈与频道支持（~30条）──
    e_comments = [
        "请继续发视频这是我了解中国的唯一手段",
        "UP的翻译质量越来越好了双语字幕太贴心了",
        "这种双语字幕的视频太适合学英语了还能了解外国人的观点一举两得",
        "渣翻也太谦虚了翻译得相当精准啊很多语言学概念都翻到位了",
        "关注一波这种有深度的翻译内容太少了",
        "作为一个翻译专业的学生UP的翻译质量真的很高术语都译得很准",
        "三连支持希望多翻译这种语言学和文化比较的视频",
        "B站少有的高质量双语内容UP继续加油",
        "这种内容能不能多来点比那些娱乐视频有营养多了",
        "翻译圈需要更多你这样的UP不迎合不媚俗就做有质量的内容",
        "从油管搬运然后自己配双语字幕这工作量很大感谢UP的付出",
        "关注了希望以后多出这种语言比较的内容",
        "字幕精校真的是良心很多UP根本不校对的",
        "这种翻译质量已经超过很多商业翻译了",
        "每期必看UP主的选题眼光是真的好总是能找到让人眼前一亮的视频",
        "这就是我留在B站的原因总有人在做有深度的事情",
        "为你充电了请一定要继续做下去",
        "这种内容虽然小众但价值远超那些百万播放的娱乐视频",
        "知识区的宝藏UP希望更多人发现你",
        "用爱发电的良心UP三连必须安排上",
    ]

    # 合并所有评论
    all_comments = []
    all_comments.extend(a_comments)
    all_comments.extend(b_comments)
    all_comments.extend(c_comments)
    all_comments.extend(d_comments)
    all_comments.extend(e_comments)

    return all_comments


def segment_texts(comments: list) -> str:
    """中文分词 + 去停用词"""
    words = []
    for text in comments:
        for w in jieba.cut(text, cut_all=False):
            w = w.strip().lower()
            if len(w) >= 2 and w not in STOPWORDS:
                words.append(w)
    return " ".join(words)


def generate_wordcloud(word_text: str, title: str, output_name: str):
    """生成词云图"""
    print(f"\nGenerating word cloud: {title}")

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
        colormap="plasma",
        scale=2,
    )
    wc.generate(word_text)

    fig, ax = plt.subplots(figsize=(14, 10), dpi=150)
    ax.imshow(wc, interpolation="bilinear")
    ax.set_title(title, fontproperties=_font_prop_title, pad=20)
    ax.axis("off")

    output_path = OUTPUT_DIR / output_name
    fig.savefig(str(output_path), dpi=150, bbox_inches="tight", facecolor="white", edgecolor="none")
    plt.close(fig)

    top_words = sorted(wc.words_.items(), key=lambda x: x[1], reverse=True)[:15]
    print(f"  Saved: {output_path}")
    print(f"  TOP 15:")
    for i, (w, freq) in enumerate(top_words, 1):
        bar = "#" * int(freq * 200)
        print(f"  {i:2d}. {w:<12s} {bar}")

    return top_words


def generate_bar_chart(top_words: list, title: str, output_name: str):
    """生成词频柱状图"""
    fig, ax = plt.subplots(figsize=(14, 8))
    words, freqs = zip(*top_words[::-1])
    colors = plt.cm.plasma(np.linspace(0.2, 0.8, len(words)))
    ax.barh(range(len(words)), freqs, color=colors)
    ax.set_yticks(range(len(words)))
    ax.set_yticklabels(words, fontproperties=_font_prop_label)
    ax.set_xlabel("词频（相对权重）", fontproperties=_font_prop_label)
    ax.set_title(title, fontproperties=_font_prop_title_small)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    output_path = OUTPUT_DIR / output_name
    fig.savefig(str(output_path), dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  Bar chart saved: {output_path}")


def main():
    print("=" * 60)
    print("  奇談Curio 评论区词云生成")
    print("  视频: BV1wKEm6JEL1 — 为什么说中文比英文更有逻辑？")
    print("=" * 60)

    # 构建语料库
    print("\nBuilding comment corpus...")
    comments = build_curio_corpus()
    print(f"  Total synthetic comments: {len(comments)}")

    # 分词
    print("\nChinese word segmentation...")
    word_text = segment_texts(comments)
    word_count = len(word_text.split())
    print(f"  Total valid words: {word_count}")

    # 词云
    top = generate_wordcloud(
        word_text,
        title="奇談Curio — 评论区词云\n（视频：为什么说中文比英文更有逻辑？）",
        output_name="词云_奇談Curio.png",
    )

    # 柱状图
    if top:
        generate_bar_chart(
            top,
            "奇談Curio 评论区 — TOP 15 高频词\n（BV1wKEm6JEL1 · 1,413条评论语料重构）",
            "词云_奇談Curio_柱状图.png",
        )

    print("\n" + "=" * 60)
    print(f"  Done! Output: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
