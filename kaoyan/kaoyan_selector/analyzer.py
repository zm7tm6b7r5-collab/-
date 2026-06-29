"""DeepSeek API 深度分析模块"""
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from prompts.analyzer_prompt import SYSTEM_PROMPT, build_analyzer_prompt
from kaoyan_selector.deepseek_client import chat_completion

logger = logging.getLogger(__name__)


def analyze_article(article, config):
    """对排名第一的文章进行全方位深度分析"""
    logger.info(f"=== 第三阶段：深度分析 ===")
    logger.info(f"文章: {article.get('title', '')}")

    score_info = (
        f"主题匹配度: {article.get('topic_match', 'N/A')}, "
        f"逻辑复杂度: {article.get('logic_complexity', 'N/A')}, "
        f"语言难度: {article.get('language_difficulty', 'N/A')}, "
        f"命题潜力: {article.get('exam_potential', 'N/A')}, "
        f"真题相似度: {article.get('exam_similarity', 'N/A')}, "
        f"综合评分: {article.get('composite_score', 'N/A')}"
    )

    user_prompt = build_analyzer_prompt(article, score_info)
    result = chat_completion(config, SYSTEM_PROMPT, user_prompt,
                             temperature=0.7, max_tokens=8192, json_mode=True)

    if not result:
        logger.error("深度分析 API 调用全部失败")
        return _fallback_analysis(article)

    return result


def _fallback_analysis(article):
    """兜底分析结果（当 API 不可用时）"""
    title = article.get("title", "Unknown")
    source = article.get("source", "Unknown")
    return {
        "recommendation_reason": f"（API 不可用，生成兜底内容）\n该文选自{source}，主题契合考研英语高频话题范畴，从标题判断具有论证深度和命题价值。建议获取 API 后重新分析。",
        "chinese_summary": f"（API 不可用，无法生成摘要）\n文章标题: {title}\n来源: {source}",
        "logic_framework": {
            "part1": "（待 API 分析）",
            "part2": "（待 API 分析）",
            "part3": "（待 API 分析）",
            "core_argument": "（待提取）",
            "author_stance": "（待判断）",
        },
        "vocabulary": [],
        "long_sentences": [],
        "mock_exam": {
            "main_idea": {"question": "（待生成）", "options": ["", "", "", ""], "answer": "", "analysis": ""},
            "vocabulary": {"question": "（待生成）", "options": ["", "", "", ""], "answer": "", "analysis": ""},
            "inference": {"question": "（待生成）", "options": ["", "", "", ""], "answer": "", "analysis": ""},
            "detail": {"question": "（待生成）", "options": ["", "", "", ""], "answer": "", "analysis": ""},
            "attitude": {"question": "（待生成）", "options": ["", "", "", ""], "answer": "", "analysis": ""},
        },
        "prediction_top10": [],
    }
