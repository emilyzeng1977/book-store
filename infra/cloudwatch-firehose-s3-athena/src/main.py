import gzip
import base64
import json
import re
from io import BytesIO

def decode_record(record):
    """解压并base64解码Firehose record"""
    compressed_payload = base64.b64decode(record["data"])
    with gzip.GzipFile(fileobj=BytesIO(compressed_payload)) as f:
        decompressed = f.read().decode("utf-8")
    return decompressed

def extract_json_from_log(log_text):
    """从CloudWatch日志里提取第一个JSON对象"""
    match = re.search(r'\{.*\}', log_text, re.DOTALL)
    if match:
        json_str = match.group(0)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            print("⚠ JSON解析失败，返回None")
            return None
    return None

def lambda_handler(event, context):
    print("Lambda invoked with event:")
    print(json.dumps(event, indent=2))

    output = []

    for record in event.get("records", []):
        try:
            payload = decode_record(record)
            print(f"Decoded payload:\n{payload}")

            # 提取 JSON
            json_data = extract_json_from_log(payload)
            if json_data is None:
                # 没有找到JSON就跳过或存空对象
                json_data = {}

            # 编码为base64后返回
            encoded_data = base64.b64encode(
                json.dumps(json_data).encode("utf-8")
            ).decode("utf-8")

            output_record = {
                "recordId": record["recordId"],
                "result": "Ok",
                "data": encoded_data
            }
            output.append(output_record)

        except Exception as e:
            print(f"Failed to decode record: {e}")
            output.append({
                "recordId": record["recordId"],
                "result": "ProcessingFailed",
                "data": record["data"]  # 原样返回
            })

    return {"records": output}
