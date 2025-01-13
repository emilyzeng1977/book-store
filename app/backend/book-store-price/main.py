from flask import Flask, jsonify, request, g
import socket

app = Flask(__name__)

@app.route('/price', methods=['GET'])
def price():
    # 获取服务器的主机名
    server_name = socket.gethostname()

    # 获取请求参数 error_host_name
    book_id = request.args.get('book_id', 'unknown')  # 默认值为 "unknown"
    traceparent = request.headers.get("traceparent")

    # 如果 book_id 是 -1，返回 500 错误
    if book_id == "-1":
        return jsonify({
            "error": "Invalid book_id",
            "message": "book_id cannot be -1"
        }), 500

    # 确定 price 值
    price = "unknown" if book_id == "unknown" else "some_price_value"  # 替换为实际逻辑

    # 获取服务器的 IP 地址
    try:
        server_ip = socket.gethostbyname(server_name)
    except socket.gaierror:
        server_ip = "127.0.0.1"  # 默认值

    # 创建响应
    response = jsonify({
        "message": "Hello, World!",
        "from price sever": {
            "book_id": book_id,
            "price": price,
            "server_name": server_name,
            "server_ip": server_ip,
            "traceparent": traceparent
        }
    })

    # 将 traceparent 放到响应头
    if traceparent:
        response.headers["traceparent"] = traceparent

    return response

@app.route('/healthz', methods=['GET'])
def health_check():
    # 这里可以添加你想要的健康检查逻辑
    # 例如，检查数据库连接或其他依赖服务是否可用
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)