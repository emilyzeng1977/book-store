from flask import Flask, jsonify
import socket

app = Flask(__name__)

@app.route('/hello', methods=['GET'])
def hello_world():
    # 获取服务器的主机名
    server_name = socket.gethostname()
    # 获取服务器的 IP 地址
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