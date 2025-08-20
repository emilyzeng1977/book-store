from flask import jsonify
from . import app

@app.route('/healthz', methods=['GET'])
def healthz_check():
    return jsonify({"status": "ok", "message": "Hello, bookStorePrice!"}), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "Hello, bookStorePrice!"}), 200
