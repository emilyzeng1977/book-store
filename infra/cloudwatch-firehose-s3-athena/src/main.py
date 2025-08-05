import gzip
import base64
import json
from io import BytesIO
from datetime import datetime

def decode_record(record):
    """解压并 base64 解码 Firehose record 成 CloudWatch Logs JSON"""
    compressed_payload = base64.b64decode(record["data"])
    with gzip.GzipFile(fileobj=BytesIO(compressed_payload)) as f:
        return json.loads(f.read().decode("utf-8"))

def extract_valid_message(event):
    """提取 message 中 JSON，并确保有 request_headers"""
    try:
        msg_obj = json.loads(event.get("message", "{}"))
    except Exception:
        return None
    if not isinstance(msg_obj, dict) or "request_headers" not in msg_obj:
        return None

    # 用 message 自带 timestamp
    ts = msg_obj.get("timestamp")
    if ts:
        try:
            msg_obj["@timestamp"] = int(datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp() * 1000)
        except Exception:
            pass

    return msg_obj

def lambda_handler(event, context):
    output = []

    for record in event.get("records", []):
        try:
            cw_data = decode_record(record)
            log_events = cw_data.get("logEvents", [])

            # 只保留有效 logEvents
            valid_messages = [extract_valid_message(e) for e in log_events]
            valid_messages = [m for m in valid_messages if m]

            if not valid_messages:
                # 全部无效，直接丢弃，不写 Unsaved/
                output.append({
                    "recordId": record["recordId"],
                    "result": "Dropped",
                    "data": record["data"]
                })
                continue

            # 拼成 JSON Lines
            payload = "\n".join(json.dumps(m, ensure_ascii=False) for m in valid_messages)
            encoded_data = base64.b64encode(payload.encode("utf-8")).decode("utf-8")

            output.append({
                "recordId": record["recordId"],
                "result": "Ok",
                "data": encoded_data
            })

        except Exception as e:
            # 出现异常也不写 Unsaved/，全部丢掉
            output.append({
                "recordId": record["recordId"],
                "result": "Dropped",
                "data": record["data"]
            })

    return {"records": output}
