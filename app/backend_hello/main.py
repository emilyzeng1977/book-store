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
            "server_ip": server_ip
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)