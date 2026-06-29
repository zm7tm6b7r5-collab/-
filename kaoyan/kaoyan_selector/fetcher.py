"""文章发现模块：RSS + 网页抓取 + 搜索"""
import json
import time
import logging
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from html import unescape

from bs4 import BeautifulSoup
from kaoyan_selector.http_utils import http_get

logger = logging.getLogger(__name__)

RSS_FEEDS = {
    "Scientific American": [
        "https://www.scientificamerican.com/rss/",
    ],
    "Nature": [
        "https://www.nature.com/nature.rss",
    ],
    "The Guardian": [
        "https://www.theguardian.com/international/rss",
    ],
    "The New York Times": [
        "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/Science.xml",
    ],
    "The Atlantic": [
        "https://www.theatlantic.com/feed/all/",
    ],
    "Time": [
        "https://time.com/rss",
    ],
    "The Washington Post": [
        "https://feeds.washingtonpost.com/rss/world",
    ],
    "The Wall Street Journal": [
        "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
    ],
    "The Christian Science Monitor": [
        "https://www.csmonitor.com/Feed/International-News",
    ],
}

# Google News 搜索 URL（作为 DuckDuckGo 的替代）
GOOGLE_NEWS_SEARCH = "https://news.google.com/rss/search"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

EXCLUDE_KEYWORDS = [
    "sport", "celebrity", "entertainment", "gossip", "stock market",
    "election campaign", "war in", "conflict", "movie review",
    "tv show", "grammy", "oscar", "nba", "nfl", "premier league",
    "athlete", "tournament", "box office", "royal family",
]

TARGET_TOPICS = [
    "artificial intelligence ethics regulation",
    "technology privacy digital society",
    "education reform university college",
    "psychology cognitive behavioral research",
    "economics policy inequality labor market",
    "business strategy innovation management",
    "environmental climate protection sustainability",
    "social change culture trend",
    "scientific discovery research breakthrough",
    "public policy government regulation",
]


def _clean_html(text):
    """清理 HTML 标签"""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    text = unescape(text)
    return text.strip()


def _is_relevant(title, description=""):
    """快速关键词过滤"""
    text = f"{title} {description}".lower()
    for kw in EXCLUDE_KEYWORDS:
        if kw in text:
            return False
    return True


def _parse_rss_date(date_str):
    """解析 RSS 日期"""
    if not date_str:
        return None
    # RSS dates are usually RFC 2822 format
    try:
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(date_str)
    except Exception:
        pass
    try:
        for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"]:
            try:
                return datetime.strptime(date_str[:19], fmt)
            except ValueError:
                continue
    except Exception:
        pass
    return None


def _is_within_days(date_obj, days=7):
    """检查日期是否在 N 天内"""
    if date_obj is None:
        return True
    return (datetime.now(date_obj.tzinfo) if date_obj.tzinfo else datetime.now()) - date_obj <= timedelta(days=days)


def _fetch_rss(config, source, feed_url):
    """从 RSS 源获取文章（使用 xml.etree）"""
    results = []
    try:
        resp = http_get(feed_url, config, timeout=20)
        if resp.status_code != 200:
            return results

        root = ET.fromstring(resp.content)

        # RSS 2.0 格式
        for item in root.iter("item"):
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            description = item.findtext("description", "")
            pub_date = item.findtext("pubDate", "")

            if title and link:
                description = _clean_html(description)
                if _is_relevant(title, description):
                    dt = _parse_rss_date(pub_date)
                    if _is_within_days(dt):
                        results.append({
                            "title": title,
                            "source": source,
                            "url": link.strip(),
                            "description": description[:500],
                            "topic": "",
                            "date": pub_date,
                        })

        # Atom 格式
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
            title_el = entry.find("{http://www.w3.org/2005/Atom}title")
            title = title_el.text if title_el is not None else ""
            link_el = entry.find("{http://www.w3.org/2005/Atom}link")
            link = link_el.get("href", "") if link_el is not None else ""
            summary_el = entry.find("{http://www.w3.org/2005/Atom}summary")
            summary = summary_el.text if summary_el is not None else ""
            updated_el = entry.find("{http://www.w3.org/2005/Atom}updated")
            updated = updated_el.text if updated_el is not None else ""

            if title and link:
                summary = _clean_html(summary)
                if _is_relevant(title, summary):
                    dt = _parse_rss_date(updated)
                    if _is_within_days(dt):
                        results.append({
                            "title": title,
                            "source": source,
                            "url": link.strip(),
                            "description": summary[:500],
                            "topic": "",
                            "date": updated,
                        })

    except ET.ParseError as e:
        logger.warning(f"RSS XML 解析失败 {feed_url}: {e}")
    except Exception as e:
        logger.warning(f"RSS 获取失败 {feed_url}: {e}")

    return results


def _search_google_news(config, source, topic, max_results=5):
    """通过 Google News RSS 搜索文章"""
    results = []
    query = f"{source} {topic}"
    try:
        from urllib.parse import quote
        url = f"{GOOGLE_NEWS_SEARCH}?q={quote(query)}&hl=en-US&gl=US&ceid=US:en"
        resp = http_get(url, config, timeout=20)
        if resp.status_code != 200:
            return results

        root = ET.fromstring(resp.content)
        count = 0
        for item in root.iter("item"):
            if count >= max_results:
                break
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            description = item.findtext("description", "")
            pub_date = item.findtext("pubDate", "")

            # Google News title format: "Title - Source"
            if " - " in title:
                title = title.rsplit(" - ", 1)[0]

            if title and link and _is_relevant(title, description):
                results.append({
                    "title": title,
                    "source": source,
                    "url": link.strip(),
                    "description": _clean_html(description)[:500],
                    "topic": topic[:30],
                    "date": pub_date,
                })
                count += 1

        time.sleep(1)  # 礼貌延迟

    except ET.ParseError as e:
        logger.warning(f"Google News XML 解析失败 {source}/{topic}: {e}")
    except Exception as e:
        logger.warning(f"Google News 搜索失败 {source}/{topic}: {e}")

    return results


def _scrape_economist(config):
    """专门抓取 The Economist 最新文章（无 RSS）"""
    results = []
    seen = set()
    try:
        urls = [
            "https://www.economist.com/science-and-technology",
            "https://www.economist.com/business",
            "https://www.economist.com/finance-and-economics",
            "https://www.economist.com/international",
            "https://www.economist.com/leaders",
        ]
        for page_url in urls:
            try:
                resp = http_get(page_url, config, timeout=30)
                if resp.status_code != 200:
                    logger.warning(f"The Economist {page_url} 返回 {resp.status_code}")
                    continue
                soup = BeautifulSoup(resp.text, "html.parser")

                # 策略1: 找所有包含文章链接的 a 标签
                for tag in soup.find_all(["a", "h2", "h3"]):
                    if tag.name == "a":
                        href = tag.get("href", "")
                        title = tag.get_text(strip=True)
                        # 尝试 aria-label
                        if not title or len(title) < 15:
                            title = tag.get("aria-label", "")
                    else:
                        link = tag.find("a")
                        if not link:
                            continue
                        href = link.get("href", "")
                        title = tag.get_text(strip=True)

                    if not href or not title:
                        continue
                    if len(title) < 15 or len(title) > 200:
                        continue
                    # Economist 文章 URL 特征
                    if not re.search(r"/(20\d{2}/\d{2}|20\d{6})", href):
                        continue
                    if not href.startswith("http"):
                        href = "https://www.economist.com" + href
                    if href in seen:
                        continue
                    if not _is_relevant(title):
                        continue

                    seen.add(href)
                    results.append({
                        "title": title,
                        "source": "The Economist",
                        "url": href,
                        "description": "",
                        "topic": "",
                        "date": "",
                    })

                # 策略2: 从 JSON-LD / schema.org 数据提取
                for script in soup.find_all("script", type="application/ld+json"):
                    try:
                        data = json.loads(script.string)
                        if isinstance(data, dict):
                            items = data.get("@graph", [data])
                        else:
                            items = data if isinstance(data, list) else []
                        for item in items:
                            if item.get("@type") in ("Article", "NewsArticle"):
                                title = item.get("headline", "")
                                url = item.get("url", "")
                                if title and url and len(title) > 15 and url not in seen:
                                    seen.add(url)
                                    results.append({
                                        "title": title,
                                        "source": "The Economist",
                                        "url": url,
                                        "description": item.get("description", "")[:500],
                                        "topic": "",
                                        "date": item.get("datePublished", ""),
                                    })
                    except (json.JSONDecodeError, AttributeError, TypeError):
                        pass

            except Exception as e:
                logger.warning(f"The Economist {page_url} 抓取异常: {e}")
            time.sleep(1)

    except Exception as e:
        logger.warning(f"The Economist 抓取失败: {e}")

    logger.info(f"The Economist 共抓到 {len(results)} 篇")
    return results


def _sample_across_sources(articles, sources, max_total=40):
    """从每个来源均匀采样，保证多样性"""
    from collections import defaultdict
    by_source = defaultdict(list)
    for a in articles:
        by_source[a["source"]].append(a)

    # 统计各来源的文章数
    logger.info("各来源文章数:")
    for src, arts in sorted(by_source.items(), key=lambda x: -len(x[1])):
        logger.info(f"  {src}: {len(arts)} 篇")

    # 计算每源配额：至少保证每个源有 floor(max_total / num_sources) 篇
    num_sources = len(sources)
    per_source_target = max(2, max_total // num_sources)

    selected = []
    # 第一轮：每个源取配额篇
    for src in sources:
        pool = by_source.get(src, [])
        selected.extend(pool[:per_source_target])

    # 第二轮：轮询各源，每次各取 1 篇，保证公平
    if len(selected) < max_total:
        remaining_slots = max_total - len(selected)
        # 构建每源的剩余池
        overflow = {}
        for src in sources:
            pool = by_source.get(src, [])
            extra = pool[per_source_target:]
            if extra:
                overflow[src] = list(extra)  # 拷贝，后续 pop(0)
        # 轮询取
        while remaining_slots > 0 and overflow:
            done = []
            for src, extras in overflow.items():
                if remaining_slots <= 0:
                    break
                selected.append(extras.pop(0))
                remaining_slots -= 1
                if not extras:
                    done.append(src)
            for src in done:
                del overflow[src]

    logger.info(f"多源采样后: {len(selected)} 篇（{len(set(a['source'] for a in selected))} 个来源）")
    return selected


def _resolve_google_news_url(url, config):
    """解析 Google News 重定向链接，获取真实文章 URL"""
    if "news.google.com/rss/articles/" not in url:
        return url

    # 策略1: HTTP 跟随重定向
    try:
        resp = http_get(url, config, timeout=15)
        if resp.url and "news.google.com" not in resp.url:
            logger.info(f"Google News URL 解析成功: {resp.url[:80]}...")
            return resp.url
    except Exception as e:
        logger.debug(f"Google News HTTP 解析失败: {e}")

    # 策略2: base64 protobuf 解码
    try:
        import base64
        import re
        match = re.search(r"/articles/([A-Za-z0-9_-]+)", url)
        if match:
            encoded = match.group(1)
            # URL-safe base64 → 标准 base64
            encoded = encoded.replace("-", "+").replace("_", "/")
            encoded += "=" * (4 - len(encoded) % 4)
            decoded = base64.b64decode(encoded)
            decoded_str = decoded.decode("latin-1")
            # 从 protobuf 中提取 http(s) URL
            urls_found = re.findall(r"https?://[^\x00-\x1f\x7f-\x9f]+", decoded_str)
            for u in urls_found:
                u = u.rstrip("\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f")
                # 过滤掉资源文件 URL，只保留文章链接
                if len(u) > 40 and not any(x in u for x in [".jpg", ".png", ".css", ".js", ".xml", "google.com", "/rss/", "schema.org"]):
                    logger.info(f"Google News base64 解码成功: {u[:80]}...")
                    return u
    except Exception as e:
        logger.debug(f"Google News base64 解码失败: {e}")

    return url


def fetch_article_content(url, config, max_chars=4000):
    """抓取单篇文章的正文内容"""
    real_url = _resolve_google_news_url(url, config)
    try:
        resp = http_get(real_url, config, timeout=20)
        if resp.status_code != 200:
            logger.warning(f"文章抓取失败 {real_url}: HTTP {resp.status_code}")
            return ""
        soup = BeautifulSoup(resp.text, "html.parser")

        # 按优先级尝试常见正文选择器
        selectors = [
            "article", "[itemprop='articleBody']", ".article-body",
            ".article-content", ".post-content", ".story-body",
            ".content-body", ".entry-content", ".c-article-body",
            "main p", ".article__body", "[data-article-body]",
        ]
        paragraphs = []
        for sel in selectors:
            container = soup.select(sel)
            if container:
                for el in container:
                    for p in el.find_all("p"):
                        text = p.get_text(strip=True)
                        if len(text) > 40 and not text.startswith("Sign up") and not text.startswith("Subscribe"):
                            paragraphs.append(text)
                if paragraphs:
                    break

        # 如果上面都没命中，回退到正文段落提取
        if not paragraphs:
            for p in soup.find_all("p"):
                text = p.get_text(strip=True)
                if len(text) > 60:
                    paragraphs.append(text)

        content = "\n\n".join(paragraphs)
        if len(content) > max_chars:
            content = content[:max_chars] + "\n\n...（正文过长，已截断）"
        return content

    except Exception as e:
        logger.warning(f"文章抓取异常 {real_url}: {e}")
        return ""


def fetch_articles(config, min_articles=20):
    """主入口：获取候选文章列表"""
    sources = config.get("target_sources", [])
    all_articles = []
    seen_urls = set()

    logger.info("=== 第一阶段：文章发现 ===")

    # 1. RSS 源
    logger.info("正在从 RSS 源获取文章...")
    for source, feeds in RSS_FEEDS.items():
        if source not in sources:
            continue
        source_before = len(all_articles)
        for feed_url in feeds:
            for art in _fetch_rss(config, source, feed_url):
                if art["url"] not in seen_urls:
                    seen_urls.add(art["url"])
                    all_articles.append(art)
            time.sleep(0.5)
        logger.info(f"  {source}: +{len(all_articles) - source_before} 篇")

    logger.info(f"RSS 获取: {len(all_articles)} 篇")

    # 2. The Economist 特殊处理（无公开 RSS）
    if "The Economist" in sources:
        logger.info("正在抓取 The Economist...")
        eco_before = len(all_articles)
        for art in _scrape_economist(config):
            if art["url"] not in seen_urls:
                seen_urls.add(art["url"])
                all_articles.append(art)
        logger.info(f"  The Economist: +{len(all_articles) - eco_before} 篇")

    # 3. Google News 搜索补充（RSS 产出少的源也搜一下，不只搜无 RSS 的）
    rss_sources = set(RSS_FEEDS.keys())
    weak_sources = [s for s in sources if s not in rss_sources and s != "The Economist"]
    # 同时给 RSS 产出少的源也做补充搜索
    source_counts = {}
    for a in all_articles:
        source_counts[a["source"]] = source_counts.get(a["source"], 0) + 1
    for s in sources:
        if s in rss_sources and source_counts.get(s, 0) < 3:
            weak_sources.append(s)
    weak_sources = list(dict.fromkeys(weak_sources))  # 去重保序

    if weak_sources:
        logger.info(f"正在通过 Google News 搜索补充（{len(weak_sources)} 个源）...")
        for source in weak_sources:
            for topic in TARGET_TOPICS[:2]:  # 每个源搜 2 个主题
                for art in _search_google_news(config, source, topic, max_results=3):
                    if art["url"] not in seen_urls:
                        seen_urls.add(art["url"])
                        all_articles.append(art)

    logger.info(f"总计发现: {len(all_articles)} 篇候选文章")

    # 4. 去重
    unique = {a["url"]: a for a in all_articles if a.get("url")}
    articles = list(unique.values())

    # 5. 按来源均匀采样（保持多样性）
    if len(articles) > 40:
        articles = _sample_across_sources(articles, sources, max_total=40)

    if len(articles) < min_articles:
        logger.warning(f"候选文章不足 {min_articles} 篇，实际: {len(articles)}")

    # 最终来源分布
    final_sources = {}
    for a in articles:
        final_sources[a["source"]] = final_sources.get(a["source"], 0) + 1
    logger.info(f"最终候选分布: {dict(sorted(final_sources.items(), key=lambda x: -x[1]))}")

    logger.info(f"最终候选: {len(articles)} 篇")
    return articles
