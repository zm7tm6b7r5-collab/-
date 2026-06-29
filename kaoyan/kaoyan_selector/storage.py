"""去重与存档管理"""
import json
import hashlib
import os
from datetime import datetime

HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "kaoyan_history.json")


def _load():
    if not os.path.exists(HISTORY_FILE):
        return {"pushed_articles": {}}
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _make_key(article):
    """生成文章唯一标识（基于 title+source 的 hash）"""
    raw = f"{article.get('title', '')}|{article.get('source', '')}"
    return hashlib.md5(raw.encode()).hexdigest()


def is_duplicate(article):
    """检查文章是否已经推送过"""
    history = _load()
    key = _make_key(article)
    return key in history["pushed_articles"]


def mark_pushed(article, score=0):
    """标记文章为已推送"""
    history = _load()
    key = _make_key(article)
    history["pushed_articles"][key] = {
        "title": article.get("title", ""),
        "source": article.get("source", ""),
        "url": article.get("url", ""),
        "pushed_date": datetime.now().strftime("%Y-%m-%d"),
        "score": score,
    }
    _save(history)


def get_history():
    """获取所有已推送文章的列表"""
    history = _load()
    return list(history["pushed_articles"].values())


def get_pushed_urls():
    """获取所有已推送文章的 URL 集合"""
    history = _load()
    return {v["url"] for v in history["pushed_articles"].values() if v.get("url")}
