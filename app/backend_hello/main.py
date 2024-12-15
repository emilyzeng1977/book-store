from flask import Flask, jsonify, request
import socket

app = Flask(__name__)

@app.route('/hello', methods=['GET'])
def hello_world():
    # 获取服务器的主机名
    server_name = socket.gethostname()
    # 获取服务器的 IP 地址

    # 获取请求参数 error_host_name
    error_host_name = request.args.get('error_host_name')
    trace_id = request.headers.get("x-b3-traceid")
    span_id = request.headers.get("x-b3-spanid")

    # 如果 error_host_name 与 server_name 相同，抛出 500 错误
    if error_host_name and error_host_name == server_name:
        return jsonify({"error": "Server name matches error_host_name, throwing 500 error."}), 500

    try:
        server_ip = socket.gethostbyname(server_name)
    except socket.gaierror:
        server_ip = "127.0.0.1"  # 默认值
    return jsonify({
        "message": "Hello, World!",
        "from": {
            "server_name": server_name,
            "server_ip": server_ip,
            "trace_id": trace_id,
            "span_id": span_id
        }
    })

@app.route('/healthz', methods=['GET'])
def health_check():
    # 这里可以添加你想要的健康检查逻辑
    # 例如，检查数据库连接或其他依赖服务是否可用
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)