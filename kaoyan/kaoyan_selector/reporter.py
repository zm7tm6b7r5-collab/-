"""Markdown 报告生成模块"""
from datetime import datetime


def generate_report(scored_articles, analysis, config):
    """生成完整的 Markdown 报告"""
    today = datetime.now().strftime("%Y-%m-%d")
    lines = []

    # ===== 标题 =====
    lines.append(f"# 考研英语外刊精选日报")
    lines.append(f"**日期：{today}**")
    lines.append("")

    # ===== 候选文章排行榜 =====
    lines.append("---")
    lines.append("")
    lines.append("## 候选文章排行榜（Top 10）")
    lines.append("")
    lines.append("| 排名 | 来源 | 标题 | 综合评分 | 主题 | 命题 | 真题 |")
    lines.append("|------|------|------|----------|------|------|------|")
    for rank, art in enumerate(scored_articles[:10], 1):
        title = art.get("title", "")[:60]
        source = art.get("source", "")
        score = art.get("composite_score", 0)
        tm = art.get("topic_match", 0)
        ep = art.get("exam_potential", 0)
        es = art.get("exam_similarity", 0)
        lines.append(f"| {rank} | {source} | {title} | **{score}** | {tm} | {ep} | {es} |")
    lines.append("")

    # ===== Top 3 入选理由 =====
    lines.append("---")
    lines.append("")
    lines.append("## Top 3 入选理由")
    lines.append("")
    top3 = [a for a in scored_articles if a.get("is_top3")][:3]
    for rank, art in enumerate(top3, 1):
        lines.append(f"### No.{rank} — {art.get('source', '')}")
        lines.append(f"**{art.get('title', '')}**")
        lines.append(f"- 综合评分：**{art.get('composite_score', 0)}**")
        lines.append(f"- 主题匹配度：{art.get('topic_match', 0)} | 逻辑复杂度：{art.get('logic_complexity', 0)} | 语言难度：{art.get('language_difficulty', 0)}")
        lines.append(f"- 命题潜力：{art.get('exam_potential', 0)} | 真题相似度：{art.get('exam_similarity', 0)}")
        lines.append(f"- 入选理由：{art.get('score_reason', '')}")
        lines.append(f"- 链接：{art.get('url', '')}")
        lines.append("")

    # ===== 今日考研英语精选外刊 =====
    lines.append("---")
    lines.append("")
    lines.append("# 今日考研英语精选外刊")
    lines.append("")

    best = scored_articles[0] if scored_articles else {}
    lines.append(f"| 项目 | 内容 |")
    lines.append(f"|------|------|")
    lines.append(f"| 日期 | {today} |")
    lines.append(f"| 来源 | {best.get('source', '')} |")
    lines.append(f"| 标题 | {best.get('title', '')} |")
    lines.append(f"| 作者 | {best.get('author', '（待获取）')} |")
    lines.append(f"| 发布时间 | {best.get('date', '（待获取）')} |")
    lines.append(f"| 原文链接 | {best.get('url', '')} |")
    lines.append(f"| 综合评分 | **{best.get('composite_score', 0)}** |")
    lines.append(f"| 真题相似度 | **{best.get('exam_similarity', 0)}** |")
    lines.append("")

    # ===== 分析内容 =====
    if analysis:
        # 推荐理由
        lines.append("---")
        lines.append("")
        lines.append("## 推荐理由")
        lines.append("")
        lines.append(analysis.get("recommendation_reason", ""))

        # 中文摘要
        lines.append("")
        lines.append("## 中文摘要")
        lines.append("")
        lines.append(analysis.get("chinese_summary", ""))

        # 逻辑框架
        lines.append("")
        lines.append("## 文章逻辑框架")
        lines.append("")
        framework = analysis.get("logic_framework", {})
        lines.append(f"**第一部分（引入）：** {framework.get('part1', '')}")
        lines.append("")
        lines.append(f"**第二部分（论证）：** {framework.get('part2', '')}")
        lines.append("")
        lines.append(f"**第三部分（结论）：** {framework.get('part3', '')}")
        lines.append("")
        lines.append(f"**核心论点：** {framework.get('core_argument', '')}")
        lines.append("")
        lines.append(f"**作者立场：** {framework.get('author_stance', '')}")

        # 高频词汇
        lines.append("")
        lines.append("## 高频词汇（考研备考重点）")
        lines.append("")
        vocab = analysis.get("vocabulary", [])
        if vocab:
            lines.append("| 单词 | 音标 | 释义 | 真题频率 |")
            lines.append("|------|------|------|----------|")
            for v in vocab[:20]:
                lines.append(
                    f"| {v.get('word', '')} | {v.get('phonetic', '')} | "
                    f"{v.get('meaning', '')} | {v.get('frequency', '')} |"
                )
        else:
            lines.append("（待 API 生成）")
        lines.append("")

        # 长难句分析
        lines.append("## 长难句分析")
        lines.append("")
        sentences = analysis.get("long_sentences", [])
        for i, s in enumerate(sentences[:5], 1):
            lines.append(f"### 长难句 {i}")
            lines.append("")
            lines.append(f"**原句：** {s.get('original', '')}")
            lines.append("")
            lines.append(f"**句法结构：** {s.get('syntax_analysis', '')}")
            lines.append("")
            lines.append(f"**翻译：** {s.get('translation', '')}")
            lines.append("")
            lines.append(f"**考点：** {s.get('exam_focus', '')}")
            lines.append("")

        # 模拟命题
        lines.append("---")
        lines.append("")
        lines.append("## 考研阅读模拟命题")
        lines.append("")
        mock = analysis.get("mock_exam", {})
        exam_sections = [
            ("主旨题", "main_idea"),
            ("词义题", "vocabulary"),
            ("推断题", "inference"),
            ("细节题", "detail"),
            ("作者态度题", "attitude"),
        ]
        for label, key in exam_sections:
            q = mock.get(key, {})
            lines.append(f"### {label}")
            lines.append("")
            lines.append(f"**题目：** {q.get('question', '（待生成）')}")
            lines.append("")
            options = q.get("options", [])
            option_labels = ["A", "B", "C", "D"]
            for oi, opt in enumerate(options):
                if opt:
                    lines.append(f"{option_labels[oi]}. {opt}")
            lines.append("")
            lines.append(f"**答案：** {q.get('answer', '')}")
            lines.append("")
            lines.append(f"**解析：** {q.get('analysis', '')}")
            lines.append("")

        # AI 预测
        lines.append("---")
        lines.append("")
        lines.append("## AI 预测：未来3个月热门命题话题 Top 10")
        lines.append("")
        predictions = analysis.get("prediction_top10", [])
        if predictions:
            lines.append("| 排名 | 话题 | 预测理由 |")
            lines.append("|------|------|----------|")
            for p in predictions:
                lines.append(f"| {p.get('rank', '')} | {p.get('topic', '')} | {p.get('reason', '')} |")
        else:
            lines.append("（待 API 生成）")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"*本报告由考研英语外刊精选系统自动生成 | {today}*")

    return "\n".join(lines)


def generate_feishu_message(scored_articles, analysis, article_content="", content_source=""):
    """生成飞书消息（精简版，适合群聊推送）"""
    best = scored_articles[0] if scored_articles else {}
    today = datetime.now().strftime("%Y-%m-%d")

    title = f"📰 今日考研英语精选外刊 | {today}"

    content = (
        f"**来源：** {best.get('source', '')}\n"
        f"**标题：** {best.get('title', '')}\n"
        f"**综合评分：** {best.get('composite_score', 0)} / 10\n"
        f"**真题相似度：** {best.get('exam_similarity', 0)} / 10\n"
        f"**链接：** {best.get('url', '')}\n"
    )

    if analysis:
        reason = analysis.get("recommendation_reason", "")
        if reason:
            content += f"\n**推荐理由：** {reason[:200]}\n"

        summary = analysis.get("chinese_summary", "")
        if summary:
            content += f"\n**摘要：** {summary[:300]}\n"

        framework = analysis.get("logic_framework", {})
        if framework:
            content += (
                f"\n**逻辑框架：**\n"
                f"- {framework.get('part1', '')}\n"
                f"- {framework.get('part2', '')}\n"
                f"- {framework.get('part3', '')}\n"
                f"\n**核心论点：** {framework.get('core_argument', '')}\n"
            )

    # 添加 Top 3 简要信息
    top3 = [a for a in scored_articles if a.get("is_top3")][:3]
    if len(top3) > 1:
        content += "\n**今日 Top 3：**\n"
        for rank, art in enumerate(top3, 1):
            content += f"{rank}. {art.get('source', '')} — {art.get('title', '')[:60]}（{art.get('composite_score', 0)}分）\n"

    return {
        "title": title,
        "content": content,
        "article_content": article_content,
        "article_content_source": content_source,
    }
