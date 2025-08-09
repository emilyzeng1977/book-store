import json
import gzip
import base64
from io import BytesIO
import uuid
import time

# 你的日志文本（直接复制你提供的那一整段）
log_message = """[2025-08-04 06:45:30,087] ERROR in routes_books: [Price Service] Error getting price for BK000008: 404 Client Error: NOT FOUND for url: http://book_store_price.local:5000/price/BK000008
{
    "timestamp": "2025-08-04T06:45:30.087860Z",
    "remote_addr": "10.0.1.4",
    "method": "GET",
    "url": "http://dev-api.be-devops.shop/books/BK000008/price",
    "status": 500,
    "duration": 0.013,
    "request_headers": {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "Host": "dev-api.be-devops.shop",
        "Content-Length": "0",
        "X-Forwarded-Port": "443",
        "X-Amzn-Trace-Id": "Root=1-6890570a-39623a5056fb3280515bae5f",
        "Sec-Ch-Ua-Platform": "\\"macOS\\"",
        "Sec-Ch-Ua": "\\"Not)A;Brand\\";v=\\"8\\", \\"Chromium\\";v=\\"138\\", \\"Google Chrome\\";v=\\"138\\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Accept": "*/*",
        "Origin": "https://dev.be-devops.shop",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://dev.be-devops.shop/",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-AU,en;q=0.9",
        "Priority": "u=1, i",
        "Forwarded": "for=124.158.17.130;host=dev-api.be-devops.shop;proto=https",
        "Via": "HTTP/1.1 AmazonAPIGateway",
        "Cookie": "Authorization=Bearer <snipped>"
    },
    "response_headers": {
        "Content-Type": "application/json",
        "Content-Length": "215"
    },
    "request_body": "",
    "response_body": "{\\n  \\"book_id\\": \\"BK000008\\",\\n  \\"changed_trace_id\\": null,\\n  \\"details\\": \\"Price not found\\",\\n  \\"error\\": \\"Failed to get price from price-service\\",\\n  \\"source\\": \\"book-store\\",\\n  \\"traceparent\\": null,\\n  \\"x_b3_trace_id\\": null\\n}\\n",
    "log.level": "ERROR",
    "error": true,
    "message": "GET /books/BK000008/price returned 500"
}
"""

# 构造 CloudWatch 的日志事件（会被 Firehose 包装）
cloudwatch_payload = {
    "messageType": "DATA_MESSAGE",
    "owner": "123456789012",
    "logGroup": "test-log-group",
    "logStream": "test-log-stream",
    "subscriptionFilters": ["test-filter"],
    "logEvents": [
        {
            "id": str(uuid.uuid4()),
            "timestamp": int(time.time() * 1000),
            "message": log_message
        }
    ]
}

cloudwatch_payload = {
    "messageType": "DATA_MESSAGE",                  # 消息类型，固定是 DATA_MESSAGE
    "owner": "961341537777",                        # AWS 账号ID（模拟值）
    "logGroup": "test-tom-log-group",               # 日志组名
    "logStream": "test-tom-log-stream",             # 日志流名
    "subscriptionFilters": ["test-tom-filter"],     # 订阅过滤器名列表
    "logEvents": [                                  # 日志事件数组
        {
            "id": str(uuid.uuid4()),                # 唯一事件ID
            "timestamp": int(time.time() * 1000),   # 时间戳，毫秒
            "message": log_message                  # 实际的日志字符串
        }
    ]
}


# 压缩 + 编码
raw_bytes = json.dumps(cloudwatch_payload).encode("utf-8")
compressed = BytesIO()
with gzip.GzipFile(fileobj=compressed, mode="w") as f:
    f.write(raw_bytes)

encoded_data = base64.b64encode(compressed.getvalue()).decode("utf-8")

# 构造 Firehose Event
firehose_event = {
    "records": [
        {
            "recordId": str(uuid.uuid4()),
            "data": encoded_data
        }
    ]
}

# 打印为 Lambda 测试事件格式
print(json.dumps(firehose_event, indent=2))
