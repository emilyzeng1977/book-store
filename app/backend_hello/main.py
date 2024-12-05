from flask import Flask, jsonify
import socket

app = Flask(__name__)

@app.route('/hello', methods=['GET'])
def hello_world():
    # 获取服务器的 IP 地址
    server_ip = socket.gethostbyname(socket.gethostname())
    return jsonify({"message": "Hello, World!", "from": server_ip})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)