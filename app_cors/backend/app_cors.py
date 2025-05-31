from flask import Flask, jsonify, request, make_response
from flask_cors import CORS

app = Flask(__name__)

# 白名单
ALLOWED_ORIGINS = {"http://localhost:3000"}

# 关闭自动处理 OPTIONS，手动控制 CORS
CORS(app, origins=ALLOWED_ORIGINS, automatic_options=False)

@app.route("/api/data", methods=["GET", "POST", "OPTIONS"])
def handle_data():
    origin = request.headers.get("Origin")

    # 处理预检请求 (OPTIONS)
    if request.method == "OPTIONS":
        if origin not in ALLOWED_ORIGINS:
            return jsonify({"error": "CORS origin not allowed"}), 403

        # 构造允许的 CORS 响应头
        response = make_response('', 204)
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Custom-Header"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Max-Age"] = "5"
        return response

    # 其他请求（GET、POST）继续保留自动检查（由 flask_cors 处理）
    if request.method == "GET":
        return jsonify({"message": "Hello from Flask (GET)!"})

    if request.method == "POST":
        if request.content_type == "application/json":
            data = request.get_json()
        elif request.content_type == "application/x-www-form-urlencoded":
            data = request.form.to_dict()
        else:
            return jsonify({"error": "Unsupported Content-Type"}), 415

        return jsonify({
            "message": "Hello from Flask (POST)!",
            "you_sent": data
        })

if __name__ == "__main__":
    app.run(port=5000)
