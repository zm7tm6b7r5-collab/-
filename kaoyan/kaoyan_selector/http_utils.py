"""HTTP 请求工具（统一代理管理）"""
import logging
import requests

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# 中国境内可直接访问的域名（不需要代理）
DIRECT_DOMAINS = [
    "api.deepseek.com",
    "open.feishu.cn",
    "pypi.org",
    "pypi.tuna.tsinghua.edu.cn",
    "files.pythonhosted.org",
]


def get_proxies(config, url=""):
    """根据配置和目标 URL 返回代理设置"""
    proxy_config = config.get("proxy", {})
    if not proxy_config.get("enabled", False):
        return {"http": None, "https": None}

    # 检查目标是否在国内直连范围内
    for domain in DIRECT_DOMAINS:
        if domain in url:
            return {"http": None, "https": None}

    http_proxy = proxy_config.get("http", "")
    https_proxy = proxy_config.get("https", http_proxy)
    return {"http": http_proxy, "https": https_proxy} if http_proxy else {"http": None, "https": None}


def http_get(url, config, headers=None, timeout=20, **kwargs):
    """发送 GET 请求"""
    if headers is None:
        headers = DEFAULT_HEADERS
    proxies = get_proxies(config, url)
    return requests.get(url, headers=headers, timeout=timeout, proxies=proxies, **kwargs)


def http_post(url, config, json_data=None, headers=None, timeout=20, **kwargs):
    """发送 POST 请求"""
    if headers is None:
        headers = DEFAULT_HEADERS
    proxies = get_proxies(config, url)
    return requests.post(url, json=json_data, headers=headers, timeout=timeout, proxies=proxies, **kwargs)
