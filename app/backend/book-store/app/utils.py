import logging
import requests
from aws_xray_sdk.core import xray_recorder

logger = logging.getLogger(__name__)


def safe_traced_request(method, url, **kwargs):
    """
    通用封装的 requests 调用，自动注入 X-Ray trace header 并开启子 segment（如有上下文）。
    - method: 'GET', 'POST', etc.
    - 支持 kwargs 中传入 headers 和 subsegment_name
    """
    subsegment_name = kwargs.pop('subsegment_name', url)
    headers = kwargs.pop('headers', {})
    headers = headers.copy()  # 避免修改外部引用

    segment = xray_recorder.current_segment()

    if segment:
        try:
            xray_recorder.inject_trace_header(headers)
            logger.debug(f"🧵 Injected trace header: {headers.get('X-Amzn-Trace-Id')}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to inject trace header: {e}")

    logger.info(f"➡️ {method} {url}")
    logger.debug(f"Request headers: {headers}")
    logger.debug(f"Other kwargs: {kwargs}")

    try:
        if segment:
            with xray_recorder.in_subsegment(subsegment_name):
                response = requests.request(method, url, headers=headers, **kwargs)
        else:
            logger.warning("⚠️ No active X-Ray segment. Proceeding without subsegment.")
            response = requests.request(method, url, headers=headers, **kwargs)

        logger.info(f"⬅️ Response [{response.status_code}] from {url}")
        return response

    except Exception as e:
        logger.exception(f"❌ Exception during {method} request to {url}: {e}")
        raise


# ✅ 快捷方法
def safe_traced_get(url, **kwargs):
    return safe_traced_request('GET', url, **kwargs)

def safe_traced_post(url, **kwargs):
    return safe_traced_request('POST', url, **kwargs)


def serialize_book(book):
    if '_id' in book:
        book['_id'] = str(book['_id'])
    return book