import json

def lambda_handler(event, context):
    print("Lambda invoked with event:")
    print(json.dumps(event, indent=2))  # 格式化打印事件

    # 不做任何处理，直接返回输入数据（Firehose Lambda transform 要求）
    return event
