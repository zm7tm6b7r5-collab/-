#!/usr/bin/env python3
"""考研英语外刊精选系统 — 主入口
用法:
    python kaoyan_daily.py              # 完整流程
    python kaoyan_daily.py --dry-run    # 仅抓取和评分，不推送
    python kaoyan_daily.py --config path/to/config.json  # 指定配置文件
"""
import json
import logging
import os
import sys
import argparse
from datetime import datetime

from kaoyan_selector.fetcher import fetch_articles, fetch_article_content
from kaoyan_selector.scorer import score_articles
from kaoyan_selector.analyzer import analyze_article
from kaoyan_selector.reporter import generate_report, generate_feishu_message
from kaoyan_selector.pusher import push_to_feishu, push_to_feishu_bitable
from kaoyan_selector.storage import is_duplicate, mark_pushed, get_pushed_urls

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def setup_logging():
    log_file = os.path.join(BASE_DIR, "kaoyan_daily.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def load_config(config_path=None):
    if config_path:
        path = config_path
    else:
        path = os.path.join(BASE_DIR, "kaoyan_config.json")

    if not os.path.exists(path):
        print(f"配置文件不存在: {path}")
        print("请复制 kaoyan_config.json 并填入你的 API Key 和 Webhook URL")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_config(config):
    api_key = config.get("deepseek_api_key", "")
    if not api_key or "your-deepseek" in api_key:
        print("错误：请先在 kaoyan_config.json 中配置 deepseek_api_key")
        return False
    return True


def filter_duplicates(articles):
    """过滤已推送过的文章"""
    pushed_urls = get_pushed_urls()
    fresh = []
    dup_count = 0
    for art in articles:
        if art.get("url") in pushed_urls or is_duplicate(art):
            dup_count += 1
        else:
            fresh.append(art)
    if dup_count:
        logging.getLogger(__name__).info(f"已过滤 {dup_count} 篇重复文章")
    return fresh


def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description="考研英语外刊精选系统")
    parser.add_argument("--dry-run", action="store_true", help="试运行模式，不推送")
    parser.add_argument("--config", type=str, help="配置文件路径")
    parser.add_argument("--skip-fetch", action="store_true", help="跳过文章抓取（使用缓存）")
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("考研英语外刊精选系统启动")
    logger.info(f"时间: {datetime.now().isoformat()}")
    logger.info("=" * 60)

    # 1. 加载配置
    config = load_config(args.config)
    if not validate_config(config):
        if args.dry_run:
            logger.warning("API Key 未配置，dry-run 模式将使用兜底评分")
        else:
            sys.exit(1)

    # 2. 文章发现
    if args.skip_fetch:
        # 尝试从缓存加载
        cache_path = os.path.join(BASE_DIR, "kaoyan_cache.json")
        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as f:
                articles = json.load(f)
            logger.info(f"从缓存加载 {len(articles)} 篇文章")
        else:
            logger.error("缓存文件不存在，无法跳过抓取")
            sys.exit(1)
    else:
        articles = fetch_articles(config, min_articles=20)
        if len(articles) < 5:
            logger.error("候选文章太少，终止流程")
            sys.exit(1)

        # 缓存文章列表
        cache_path = os.path.join(BASE_DIR, "kaoyan_cache.json")
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        logger.info(f"已缓存 {len(articles)} 篇文章到 kaoyan_cache.json")

    # 3. 去重
    articles = filter_duplicates(articles)
    if len(articles) < 3:
        logger.error("去重后文章太少，终止流程")
        sys.exit(1)

    # 4. 评分
    scored = score_articles(articles, config)
    if not scored:
        logger.error("评分结果为空，终止流程")
        sys.exit(1)

    # 5. 输出排行榜
    logger.info("\n" + "=" * 60)
    logger.info("候选文章排行榜（Top 10）")
    logger.info("=" * 60)
    for rank, art in enumerate(scored[:10], 1):
        logger.info(
            f"  {rank:2d}. [{art.get('composite_score', 0):.1f}] "
            f"{art.get('source', ''):25s} {art.get('title', '')[:60]}"
        )

    # 6. 深度分析（排名第一的文章）
    best = scored[0]
    logger.info(f"\n深度分析: {best.get('title', '')}")
    analysis = analyze_article(best, config)

    # 6.5 抓取原文（优先用非 Google News 链接的高分文章）
    article_content = ""
    content_source = ""
    for art in scored:
        url = art.get("url", "")
        if not url:
            continue
        if "news.google.com" in url:
            continue
        logger.info(f"正在抓取文章原文 [{art.get('source')}]: {art.get('title', '')[:50]}")
        article_content = fetch_article_content(url, config)
        if article_content:
            content_source = art.get("source", "")
            logger.info(f"原文抓取成功，{len(article_content)} 字符")
            break
        logger.warning("原文抓取失败，尝试下一篇...")

    if not article_content:
        logger.warning("无法获取任何文章原文")

    # 7. 生成报告
    report = generate_report(scored, analysis, config)
    report_path = os.path.join(BASE_DIR, f"kaoyan_report_{datetime.now().strftime('%Y%m%d')}.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    logger.info(f"报告已保存: {report_path}")

    # 8. 推送
    if args.dry_run:
        logger.info("试运行模式，跳过推送")
        print("\n" + "=" * 60)
        print("DRY RUN — 未推送。报告内容预览：")
        print("=" * 60)
        try:
            print(report[:3000])
        except UnicodeEncodeError:
            print(report[:3000].encode('utf-8', errors='replace').decode('utf-8', errors='replace'))
    else:
        # 飞书群推送
        feishu_msg = generate_feishu_message(scored, analysis, article_content, content_source)
        webhook_url = config.get("feishu_webhook_url", "")
        push_ok = push_to_feishu(feishu_msg, webhook_url, config)

        # 飞书多维表格存档
        bitable_ok = push_to_feishu_bitable(best, analysis, config)

        # 标记已推送
        if push_ok or bitable_ok:
            mark_pushed(best, score=best.get("composite_score", 0))

        logger.info(
            f"推送结果: 飞书群={'OK' if push_ok else '失败/跳过'}, "
            f"多维表格={'OK' if bitable_ok else '失败/跳过'}"
        )

    logger.info("=" * 60)
    logger.info("考研英语外刊精选系统执行完毕")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
