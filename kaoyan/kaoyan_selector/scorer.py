"""DeepSeek API 评分模块"""
import json
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from prompts.scorer_prompt import SYSTEM_PROMPT, build_scoring_prompt
from kaoyan_selector.deepseek_client import chat_completion

logger = logging.getLogger(__name__)


def score_articles(articles, config):
    """对文章列表进行考研英语适配度评分，返回按综合评分排序的结果"""
    if not articles:
        logger.error("没有文章可供评分")
        return []

    logger.info(f"=== 第二阶段：文章评分（共 {len(articles)} 篇）===")

    weights = config.get("scoring_weights", {
        "topic_match": 0.20, "logic_complexity": 0.20,
        "language_difficulty": 0.15, "exam_potential": 0.25, "exam_similarity": 0.20,
    })

    user_prompt = build_scoring_prompt(articles)
    result_json = chat_completion(config, SYSTEM_PROMPT, user_prompt,
                                  temperature=0.3, max_tokens=4096, json_mode=True)

    if not result_json:
        logger.error("评分 API 调用失败，使用规则兜底评分")
        return _fallback_scoring(articles, weights)

    return _parse_results(articles, result_json, weights)


def _parse_results(articles, result_json, weights):
    """解析 API 返回的评分结果"""
    scored = []
    api_articles = result_json.get("articles", [])
    top3_indices = set(result_json.get("top3", []))

    for item in api_articles:
        idx = item.get("index", 0)
        if idx >= len(articles):
            continue

        tm = item.get("topic_match", 5)
        lc = item.get("logic_complexity", 5)
        ld = item.get("language_difficulty", 5)
        ep = item.get("exam_potential", 5)
        es = item.get("exam_similarity", 5)

        composite = (
            tm * weights["topic_match"]
            + lc * weights["logic_complexity"]
            + ld * weights["language_difficulty"]
            + ep * weights["exam_potential"]
            + es * weights["exam_similarity"]
        )

        art = dict(articles[idx])
        art.update({
            "topic_match": tm,
            "logic_complexity": lc,
            "language_difficulty": ld,
            "exam_potential": ep,
            "exam_similarity": es,
            "composite_score": round(composite, 1),
            "score_reason": item.get("reason", ""),
            "is_top3": idx in top3_indices,
        })
        scored.append(art)

    scored.sort(key=lambda x: x["composite_score"], reverse=True)
    return scored


def _fallback_scoring(articles, weights):
    """规则兜底评分（当 API 不可用时）"""
    logger.warning("使用规则兜底评分")

    priority_sources = {
        "The Economist": 9, "The Atlantic": 9, "Scientific American": 8,
        "Nature": 8, "The Guardian": 7, "The New York Times": 7,
        "The Washington Post": 6, "The Wall Street Journal": 6,
        "Time": 5, "The Christian Science Monitor": 5, "The Times": 5,
    }
    topic_bonus = {
        "AI": 2, "技术伦理": 2, "心理学": 2, "经济学": 2,
        "科学发现": 2, "社会文化": 1, "教育改革": 2, "环境": 1,
    }

    scored = []
    for art in articles:
        base = priority_sources.get(art.get("source", ""), 5)
        bonus = topic_bonus.get(art.get("topic", ""), 0)
        desc_len = len(art.get("description", ""))
        length_bonus = 1 if 300 < desc_len < 800 else 0

        score = min(10, base + bonus + length_bonus) / 10 * 10
        art_copy = dict(art)
        art_copy.update({
            "topic_match": min(10, base),
            "logic_complexity": 5,
            "language_difficulty": 6,
            "exam_potential": 6,
            "exam_similarity": min(10, base + 1),
            "composite_score": round(score, 1),
            "score_reason": "规则兜底评分",
            "is_top3": False,
        })
        scored.append(art_copy)

    scored.sort(key=lambda x: x["composite_score"], reverse=True)
    for i in range(min(3, len(scored))):
        scored[i]["is_top3"] = True
    return scored
