from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)

# 允许所有域访问，或使用 CORS(app, origins=["http://localhost:3000"])
CORS(app)

@app.route("/api/data")
def get_data():
    return jsonify({"message": "Hello from Flask!"})

if __name__ == "__main__":
    app.run(port=5000)