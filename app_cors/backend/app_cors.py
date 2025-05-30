from flask import Flask, jsonify, request, make_response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 默认自动处理 OPTIONS 请求

@app.route("/api/data", methods=["GET", "POST", "OPTIONS"])
def handle_data():
    if request.method == "OPTIONS":
        return make_response('', 204)  # 明确返回 No Content 响应

    elif request.method == "GET":
        return jsonify({"message": "Hello from Flask (GET)!"})

    elif request.method == "POST":
        data = request.get_json()
        return jsonify({
            "message": "Hello from Flask (POST)!",
            "you_sent": data
        })

if __name__ == "__main__":
    app.run(port=5000)
