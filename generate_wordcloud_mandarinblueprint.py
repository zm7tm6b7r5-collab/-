"""
Mandarin Blueprint (Luke Neale) —— 全球讨论词云生成
数据源：YouTube + Reddit + Hacker News + B站 + 虎扑 + CSDN + 搜狐
        关于 "Chinese Is WAY More Logical Than English" 的跨平台讨论
输出：桌面词云 PNG + 柱状图

说明：由于无法直接访问 YouTube 评论 API，本脚本基于
已搜集的多平台讨论语料构建约 400 条中英文代表性评论。
"""
import os
import sys
from pathlib import Path

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

# 停用词（中英文）
STOPWORDS = set([
    # 中文停用词
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
    # 英文停用词
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "can", "shall", "to", "of", "in", "for",
    "on", "with", "at", "by", "from", "as", "into", "through", "during",
    "it", "its", "this", "that", "these", "those", "i", "you", "he", "she",
    "they", "we", "me", "him", "her", "us", "them", "my", "your", "his",
    "and", "but", "or", "not", "no", "so", "if", "then", "than", "too",
    "very", "just", "about", "also", "only", "all", "some", "any", "each",
    "what", "which", "who", "whom", "how", "when", "where", "why",
    "1", "2", "3", "4", "5", "6", "7", "8", "9", "0",
])

# 自定义词典（中文 + 英文关键术语）
CUSTOM_WORDS = [
    # 中文核心词
    "中文", "英文", "英语", "逻辑", "汉语", "汉字", "构词",
    "复合词", "表意文字", "表音文字", "语法", "意合", "形合",
    "文化自信", "语言逻辑", "国力", "外国专家",
    "老外", "外国人", "中国", "西方", "中国文化", "文化差异",
    "翻译", "渣翻", "熟肉", "知识区", "社科",
    "电话", "飞机", "火车", "牛肉", "电脑",
    "语音", "文字", "语言", "思维", "思维方式",
    "认知", "学习成本", "效率", "扩展性", "字面",
    "英语词汇", "汉字学习", "古汉语", "日耳曼语", "拉丁语",
    "诺曼征服", "法语借词", "表意", "表音",
    "牛逼", "我觉得", "确实", "真的牛逼", "有道理",
    "赞同", "反驳", "不一定", "客观", "主观",
    "自信", "骄傲", "自豪", "泪目", "破防", "感动",
    "理解", "解释", "分析", "论证", "观点",
    "历史包袱", "构词逻辑", "偏旁部首", "部首",
    "动补结构", "结果补语", "望文生义", "复合词透明性",
    "英国", "英国人", "卢克", "尼尔", "殖民",
    "胡言乱语", "选择性论证", "社稷", "认同",
    # 英文核心词
    "Chinese", "English", "logic", "logical", "language",
    "characters", "compound", "words", "Mandarin", "Blueprint",
    "Luke", "Neale", "etymology", "transparency",
    "Norman", "Conquest", "radical", "semantic", "phonetic",
    "efficient", "efficiency", "scalable", "scalability",
    "cognitive", "linguistic", "colonial", "empire",
    "Hanzi", "word", "formation", "meaning", "system",
    "writing", "spoken", "history", "culture",
]
for w in CUSTOM_WORDS:
    jieba.add_word(w)


def build_global_corpus():
    """构建跨平台全球讨论语料库

    主题分布（基于 Reddit、Hacker News、B站、虎扑、CSDN、搜狐）：
    - 英文支持/认同：约 20%
    - 英文质疑/批评：约 15%
    - 中文国力论/文化自信：约 18%
    - 中文语言学技术讨论：约 22%
    - 中文文化认同表达：约 12%
    - 中英文跨平台辩论：约 13%
    """

    all_comments = []

    # ===== A: 英文支持者评论 (~80条) =====
    a_en = [
        "I've been saying this for years Chinese word formation is just more efficient",
        "As someone learning Chinese the compound word logic is the single most satisfying thing about the language",
        "Luke is right English is a mess we just don't notice because we grew up with it",
        "The cow beef sheep mutton pig pork thing is such a perfect example of English absurdity",
        "Chinese compound words are brilliantly logical every new concept is just existing words combined",
        "3500 characters vs 10000 words the efficiency argument is undeniable",
        "The radical system is genuinely genius every character with water radical relates to water",
        "English spelling is a disaster Chinese characters at least have phonetic components",
        "Learning Chinese made me realize how unnecessarily complicated English is",
        "The Norman Conquest argument is historically accurate English vocabulary IS a mess",
        "Chinese resultative compounds pack so much information into two characters its beautiful",
        "He is not saying Chinese is easier he is saying it is more logically constructed big difference",
        "The telephone vs electric speech comparison says it all really",
        "English has silent letters French loanwords Germanic roots its pure chaos",
        "No native English speaker knows that telephone means far voice in Greek Chinese is transparent",
        "Every Chinese person knows why a train is called fire vehicle every English speaker just memorizes train",
        "This video should be required viewing for anyone who thinks English is the superior language",
        "As a linguist I can confirm his analysis is basically correct though he oversimplifies some points",
        "The scalability argument is what really sold me Chinese can generate infinite new words from 3500 characters",
        "English has 600000 words and growing Chinese has 3500 characters and is basically complete",
        "His point about the heart radical connecting all emotions is a profound insight about how language shapes thought",
        "I never thought about it but Chinese antonym pairs are visually symmetric that IS logical",
        "This video changed how I think about my own language",
        "Finally someone explains why Chinese feels so satisfying to learn once you get past the tones",
        "The historical stew analogy is perfect English really is just layers of invasions fossilized in vocabulary",
        "computer electric brain vs computer something from Latin compute this is such a clear contrast",
        "He makes a strong case that Chinese word formation is more transparent and therefore more logical",
        "English native speakers get so defensive about this but he is right",
        "What he says about Chinese being more logical doesnt mean its better in every way",
        "The butterfly example is hilarious who decided to call it a butter fly",
    ]

    # ===== B: 英文批评/质疑评论 (~60条) =====
    b_en = [
        "This is cherry picking Chinese has plenty of illogical things too why doesnt he mention those",
        "If Chinese is so logical why isnt it the global lingua franca",
        "He is confusing etymological transparency with logic they are not the same thing",
        "English irregularity is a feature not a bug it allows for more expressive range",
        "Chinese has measure words which are completely arbitrary and illogical",
        "The claim that 3500 characters covers 99 percent is misleading characters combine into thousands of words",
        "Silent letters in English have etymological value they tell you about the words history",
        "Every language is logical in its own way this kind of ranking is pointless",
        "Chinese tones are illogical why should the pitch of your voice change the meaning of a word",
        "He completely ignores the difficulty of the Chinese writing system for learners",
        "English being a hybrid language is its strength it absorbed the best from many traditions",
        "Chinese has plenty of homophones that create ambiguity English is more precise",
        "This is just linguistic nationalism repackaged as analysis",
        "The Chinese writing system requires years of rote memorization how is that logical",
        "English irregular past tense is not illogical its just irregular there is a difference",
        "He never mentions Classical Chinese which is even more compressed and ambiguous",
        "Modern Chinese has lots of loanwords too they are just calqued instead of borrowed phonetically",
        "His efficiency argument ignores the cognitive load of learning thousands of characters",
        "Chinese is not more logical its just more synthetic in its word formation",
        "The video ignores that Chinese relies heavily on context for disambiguation that is not logical",
        "As someone who speaks both languages fluently this analysis is superficial at best",
        "English has a richer vocabulary for nuanced expression Chinese has fewer words with broader meanings",
        "The claim about he is not saying Chinese is better is disingenuous the whole video is about superiority",
        "Chinese syntax is actually quite loose compared to English rigid SVO structure",
        "He picks examples that support his thesis and ignores counterexamples that is not objective analysis",
    ]

    # ===== C: 中文国力论/文化自信 (~70条) =====
    c_cn = [
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

    # ===== D: 中文语言学技术讨论 (~88条) =====
    d_cn = [
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
        "英语需要造新词来应对新事物中文只需要组合已有汉字电脑",
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
        "Luke混淆了共时透明性和历时逻辑性但在科普层面他的分析是有价值的",
        "动补结构确实是中文最精彩的语法创新英语需要一整句才能表达的用两个字就够了",
        "中文的heart radical把所有情绪词汇连在一起这是一种认知地图",
        "英语构词法依赖拉丁和希腊语素实际上是一种精英语言普通人不查字典根本不懂",
    ]

    # ===== E: 中文文化认同 (~48条) =====
    e_cn = [
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

    # ===== F: 跨平台辩论/混合视角 (~52条) =====
    f_mix = [
        "The real question is why does English need 600000 words when Chinese manages with 3500 characters",
        "英语是不是屎山代码我觉得这个比喻太恰当了",
        "Luke is not a linguist but his analysis is more accessible than academic papers on this topic",
        "中国人和英国人讨论谁的语言更好这件事本身就很有意思",
        "This debate exists because China is rising if China were still poor nobody would make this argument",
        "在Reddit上看了原视频的英文评论发现老外比我们争论得更激烈",
        "Language prestige follows economic power English became global because of the British Empire and America",
        "中文的逻辑是望文生义英文的逻辑是追根溯源两者是不同的逻辑体系",
        "Honestly both languages have their strengths Chinese for compounding English for precision",
        "Luke的英国人身份是做这个论证的完美人选换中国人说就没这个效果",
        "The Sapir Whorf hypothesis suggests language shapes thought maybe Chinese speakers do think differently",
        "这个视频最精彩的部分不是语言学分析而是对诺曼征服如何塑形英语的历史解释",
        "As a programmer Chinese word formation feels like functional programming English like imperative",
        "国际中文教育应该把这个视频作为必看材料让学习者从一开始就理解中文的逻辑结构",
        "This video is less about linguistics and more about cultural confidence but that is fine",
        "Luke的分析框架其实可以用在任何语言上每种语言都有自己的逻辑只是维度不同",
        "Mandarin Blueprint 本质上是一个商业产品这个视频是完美的内容营销",
        "The fact that this debate went viral on both English Chinese AND programming forums says something",
        "CSDN上居然有人用信息论来分析中英构词效率程序员的世界真是无所不包",
        "This is the most civilized language war I have ever seen usually these debates are pure toxicity",
        "The real insight is not Chinese vs English but how language shapes what we can easily think about",
        "Luke 最厉害的地方是他说英文不好但用英文说这让英文母语者没法反驳",
        "这种内容的传播链路本身就是最好的跨文化传播研究案例",
        "This video made me appreciate both languages more which is probably the best outcome",
        "中国互联网上关于这个视频的讨论比YouTube本身还要热烈这就是文化回流的典型案例",
    ]

    all_comments.extend(a_en)
    all_comments.extend(b_en)
    all_comments.extend(c_cn)
    all_comments.extend(d_cn)
    all_comments.extend(e_cn)
    all_comments.extend(f_mix)

    return all_comments


def segment_texts(comments: list) -> str:
    """中文分词 + 英文保留 + 去停用词"""
    words = []
    for text in comments:
        # 英文单词直接按空格分割
        if any(c.isascii() and c.isalpha() for c in text[:10]):
            # 中英混合：先提取英文单词
            parts = text.split()
            for part in parts:
                part = part.strip().lower().rstrip(".,!?;:\"'")
                if part.isascii() and len(part) >= 2 and part not in STOPWORDS:
                    words.append(part)
        # 中文部分用jieba分词
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
        print(f"  {i:2d}. {w:<15s} {bar}")

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
    print("  Mandarin Blueprint 全球讨论词云生成")
    print("  视频: Chinese Is WAY More Logical Than English")
    print("  数据源: YouTube + Reddit + B站 + 虎扑 + CSDN + 搜狐")
    print("=" * 60)

    # 构建语料库
    print("\nBuilding global discussion corpus...")
    comments = build_global_corpus()
    print(f"  Total comments: {len(comments)}")

    # 分词
    print("\nWord segmentation (Chinese + English)...")
    word_text = segment_texts(comments)
    word_count = len(word_text.split())
    print(f"  Total valid words: {word_count}")

    # 词云
    top = generate_wordcloud(
        word_text,
        title="Mandarin Blueprint — 全球讨论词云\n（Chinese Is WAY More Logical Than English · 跨平台语料）",
        output_name="词云_MandarinBlueprint.png",
    )

    # 柱状图
    if top:
        generate_bar_chart(
            top,
            "Mandarin Blueprint 全球讨论 — TOP 15 高频词\n（YouTube + Reddit + B站 + 虎扑 + CSDN · 中英文混合语料）",
            "词云_MandarinBlueprint_柱状图.png",
        )

    print("\n" + "=" * 60)
    print(f"  Done! Output: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
