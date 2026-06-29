"""飞书推送模块"""
import json
import logging
from kaoyan_selector.http_utils import http_post, get_proxies
import requests as req_lib  # 仅用于兜底

logger = logging.getLogger(__name__)


def push_to_feishu(message, webhook_url, config=None):
    """通过飞书 Webhook 推送消息到群聊"""
    if not webhook_url or "your-webhook-token" in webhook_url:
        logger.warning("飞书 Webhook URL 未配置，跳过推送")
        return False

    if config is None:
        config = {}

    elements = [
        {
            "tag": "markdown",
            "content": message.get("content", "")[:8000],
        }
    ]

    article_content = message.get("article_content", "")
    article_source = message.get("article_content_source", "")
    if article_content:
        elements.append({"tag": "hr"})
        source_note = f"（来源：{article_source}）\n\n" if article_source else ""
        elements.append({
            "tag": "markdown",
            "content": f"**📖 原文**{source_note}\n\n{article_content[:6000]}",
        })

    payload = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": message.get("title", "考研英语精选外刊")},
                "template": "blue",
            },
            "elements": elements,
        },
    }

    try:
        resp = http_post(webhook_url, config, json_data=payload, timeout=15)
        result = resp.json()
        if result.get("code") == 0:
            logger.info("飞书消息推送成功")
            return True
        else:
            logger.error(f"飞书推送失败: {result}")
            return False
    except Exception as e:
        logger.error(f"飞书推送异常: {e}")

        # 尝试用简单文本消息兜底
        try:
            fallback_text = f"{message.get('title', '')}\n\n{message.get('content', '')}"
            article_content = message.get("article_content", "")
            if article_content:
                fallback_text += f"\n\n---\n📖 原文：\n\n{article_content}"
            fallback = {
                "msg_type": "text",
                "content": {
                    "text": fallback_text[:20000]
                },
            }
            proxies = get_proxies(config, webhook_url)
            resp = req_lib.post(webhook_url, json=fallback, timeout=15, proxies=proxies)
            if resp.json().get("code") == 0:
                logger.info("飞书消息（文本模式）推送成功")
                return True
        except Exception:
            pass

        return False


def push_to_feishu_bitable(article, analysis, config):
    """存档到飞书多维表格（可选功能）"""
    app_id = config.get("feishu_app_id", "")
    app_secret = config.get("feishu_app_secret", "")
    bitable_app_token = config.get("feishu_bitable_app_token", "")
    table_id = config.get("feishu_bitable_table_id", "")

    if not all([app_id, app_secret, bitable_app_token, table_id]):
        logger.info("飞书多维表格未配置，跳过存档")
        return False

    # 获取 tenant_access_token
    try:
        token_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        resp = http_post(token_url, config, json_data={
            "app_id": app_id, "app_secret": app_secret
        }, timeout=15)
        token = resp.json().get("tenant_access_token", "")
    except Exception as e:
        logger.error(f"获取飞书 token 失败: {e}")
        return False

    if not token:
        return False

    # 写入记录
    try:
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")

        record_url = (
            f"https://open.feishu.cn/open-apis/bitable/v1/apps/{bitable_app_token}"
            f"/tables/{table_id}/records"
        )
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        fields = {
            "日期": today,
            "来源": article.get("source", ""),
            "标题": article.get("title", "")[:200],
            "主题": article.get("topic", ""),
            "综合评分": article.get("composite_score", 0),
            "真题相似度": article.get("exam_similarity", 0),
            "原文链接": article.get("url", ""),
        }
        resp = http_post(record_url, config, json_data={"fields": fields}, headers=headers, timeout=15)
        if resp.json().get("code") == 0:
            logger.info("飞书多维表格存档成功")
            return True
        else:
            logger.warning(f"多维表格存档失败: {resp.json()}")
            return False
    except Exception as e:
        logger.error(f"多维表格存档异常: {e}")
        return False
