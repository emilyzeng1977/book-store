from flask import Flask, jsonify, request
import socket
import timeout_decorator

app = Flask(__name__)

@timeout_decorator.timeout(2, use_signals=False)  # 超时设为1秒
@app.route('/price', methods=['GET'])
def price():
    # 获取服务器的主机名
    server_name = socket.gethostname()

    # 获取请求参数 error_host_name
    book_id = request.args.get('book_id', 'unknown')  # 默认值为 "unknown"
    traceparent = request.headers.get("traceparent") # OpenTelemetry
    x_b3_traceId = request.headers.get("X-B3-TraceId") # Zipkin

    # 确定 price 值
    price = "unknown" if book_id == "unknown" else "some_price_value"  # 替换为实际逻辑

    # 获取服务器的 IP 地址
    try:
        server_ip = socket.gethostbyname(server_name)
    except socket.gaierror:
        server_ip = "127.0.0.1"  # 默认值

    changed_traceparent = traceparent
    if traceparent:
        parts = traceparent.split("-")
        if len(parts) >= 3:
            changed_traceparent = parts[1]

    # Handle special case for `book_id`
    if book_id == "-1":
        response = jsonify({
            "error": "Invalid book_id",
            "message": "book_id cannot be -1",
            "traceparent": traceparent,
            "x_b3_traceId": x_b3_traceId,
        })
        if traceparent:
            response.headers["traceparent"] = changed_traceparent
        if x_b3_traceId:
            response.headers["x_b3_traceId"] = x_b3_traceId
        return response, 500

    # 创建响应
    response = jsonify({
        "message": "Hello, World!",
        "from price sever": {
            "book_id": book_id,
            "price": price,
            "server_name": server_name,
            "server_ip": server_ip,
            "traceparent": traceparent,
            "x_b3_traceId": x_b3_traceId
        }
    })

    # 将 traceparent 放到响应头
    if traceparent:
        response.headers["traceparent"] = changed_traceparent

    if x_b3_traceId:
        response.headers["x_b3_traceId"] = x_b3_traceId

    return response

@app.route('/healthz', methods=['GET'])
def health_check():
    # 这里可以添加你想要的健康检查逻辑
    # 例如，检查数据库连接或其他依赖服务是否可用
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)