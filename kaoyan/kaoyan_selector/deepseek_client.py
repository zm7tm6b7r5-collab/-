"""DeepSeek API 客户端"""
import json
import logging
from kaoyan_selector.http_utils import http_post, get_proxies

logger = logging.getLogger(__name__)


def chat_completion(config, system_prompt, user_prompt, temperature=0.3, max_tokens=4096, json_mode=True):
    """调用 DeepSeek Chat API，返回解析后的 JSON 或文本"""
    api_key = config.get("deepseek_api_key", "")
    if not api_key or "your-deepseek" in api_key or "your-" in api_key:
        logger.warning("API Key 未配置，跳过 API 调用")
        return None

    base_url = config.get("deepseek_base_url", "https://api.deepseek.com").rstrip("/")
    model = config.get("deepseek_model", "deepseek-chat")
    url = f"{base_url}/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if json_mode:
        body["response_format"] = {"type": "json_object"}

    for attempt in range(3):
        try:
            proxies = get_proxies(config, url)
            resp = http_post(url, config, json_data=body, headers=headers, timeout=120)
            if resp.status_code != 200:
                logger.warning(f"API 返回 {resp.status_code}: {resp.text[:300]}")
                if attempt < 2:
                    continue
                return None

            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            logger.info(
                f"API 调用成功，tokens: {usage.get('total_tokens', 'N/A')} "
                f"(prompt: {usage.get('prompt_tokens', 'N/A')}, "
                f"completion: {usage.get('completion_tokens', 'N/A')})"
            )

            if json_mode:
                try:
                    return json.loads(content)
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON 解析失败 (attempt {attempt + 1}): {e}")
                    if attempt < 2:
                        continue
                    return None
            return content

        except Exception as e:
            logger.warning(f"API 调用异常 (attempt {attempt + 1}): {e}")

    return None
