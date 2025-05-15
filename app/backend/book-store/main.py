import logging
import os
import socket

import requests
from bson.objectid import ObjectId
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient, errors

# Flask 应用初始化
app = Flask(__name__)

# 跨域支持，开发阶段全开放，生产环境建议指定域名
CORS(app)

# 日志配置，INFO级别，方便查看运行信息
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

def get_env_variable(key: str, default_value: str) -> str:
    """获取环境变量，若未设置则使用默认值"""
    value = os.getenv(key)
    return value if value else default_value

# ----------------------
# MongoDB Atlas 配置参数（可通过环境变量覆盖）
# ----------------------
atlas_mongo_user = get_env_variable("ATLAS_MONGO_USER", "tom")
atlas_mongo_password = get_env_variable("ATLAS_MONGO_PASSWORD", "abc123456")
atlas_mongo_host = get_env_variable("ATLAS_MONGO_HOST", "emily-demo.unlcmad.mongodb.net")
atlas_mongo_app_name = get_env_variable("ATLAS_MONGO_APP_NAME", "emily-demo")
atlas_mongo_db = get_env_variable("ATLAS_MONGO_DB", "book-store")

# 生成 MongoDB 连接字符串
atlas_mongo_uri = (
    f"mongodb+srv://{atlas_mongo_user}:{atlas_mongo_password}@{atlas_mongo_host}"
    f"/?retryWrites=true&w=majority&appName={atlas_mongo_app_name}"
)

# 初始化 MongoDB 连接
try:
    client = MongoClient(atlas_mongo_uri, serverSelectionTimeoutMS=3000)  # 3秒连接超时
    db = client[atlas_mongo_db]
    collection = db.books
    logging.info(f"Connected to MongoDB database: {atlas_mongo_db}")
except Exception as e:
    logging.error(f"Error connecting to MongoDB: {e}")
    raise

# ----------------------
# 路由定义
# ----------------------

@app.route('/greet', methods=['GET'])
def greet():
    """
    简单的问候接口，返回传入的名字和服务器IP
    示例: /greet?name=Tom
    """
    name = request.args.get('name', 'World')
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except socket.gaierror:
        local_ip = "127.0.0.1"

    greeting_message = f"Hello, {name}! This server's IP address is {local_ip}."
    return jsonify({'message': greeting_message})

@app.route('/books', methods=['GET'])
def get_books():
    """
    获取所有书籍列表，设置查询超时1秒
    返回格式:
    {
      "books": [
        {"_id": "...", "title": "...", "author": "..."},
        ...
      ]
    }
    """
    try:
        books = []
        for book in collection.find().max_time_ms(1000):
            book['_id'] = str(book['_id'])
            books.append(book)
        return jsonify({'books': books})
    except errors.ExecutionTimeout:
        return jsonify({'error': 'Query timed out'}), 504
    except errors.PyMongoError as e:
        logging.error(f"MongoDB query error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/books/<string:book_id>', methods=['GET'])
def get_book(book_id):
    """
    根据书籍ID获取书籍详情
    """
    try:
        obj_id = ObjectId(book_id)
    except Exception:
        return jsonify({'error': 'Invalid book ID'}), 400

    book = collection.find_one({'_id': obj_id})
    if book:
        book['_id'] = str(book['_id'])
        return jsonify(book)
    return jsonify({'error': 'Book not found'}), 404


@app.route('/books', methods=['POST'])
def add_book():
    """
    添加一本新书，要求传入 JSON，必须包含title和author字段
    """
    if not request.json or 'title' not in request.json or 'author' not in request.json:
        return jsonify({'error': 'The new book must have a title and author'}), 400

    new_book = {
        'title': request.json['title'],
        'author': request.json['author']
    }
    try:
        result = collection.insert_one(new_book)
    except errors.PyMongoError as e:
        logging.error(f"MongoDB insert error: {e}")
        return jsonify({'error': 'Failed to add book'}), 500

    new_book['_id'] = str(result.inserted_id)
    return jsonify(new_book), 201


@app.route('/books/<string:book_id>', methods=['PUT'])
def update_book(book_id):
    """
    根据书籍ID更新书籍信息，支持title和author字段更新
    """
    try:
        obj_id = ObjectId(book_id)
    except Exception:
        return jsonify({'error': 'Invalid book ID'}), 400

    if not request.json:
        return jsonify({'error': 'Invalid request, JSON body required'}), 400

    update_data = {}
    if 'title' in request.json:
        if not isinstance(request.json['title'], str):
            return jsonify({'error': 'Invalid title'}), 400
        update_data['title'] = request.json['title']

    if 'author' in request.json:
        if not isinstance(request.json['author'], str):
            return jsonify({'error': 'Invalid author'}), 400
        update_data['author'] = request.json['author']

    if not update_data:
        return jsonify({'error': 'No valid fields to update'}), 400

    try:
        result = collection.update_one({'_id': obj_id}, {'$set': update_data})
    except errors.PyMongoError as e:
        logging.error(f"MongoDB update error: {e}")
        return jsonify({'error': 'Failed to update book'}), 500

    if result.matched_count == 0:
        return jsonify({'error': 'Book not found'}), 404

    book = collection.find_one({'_id': obj_id})
    book['_id'] = str(book['_id'])
    return jsonify(book)


@app.route('/books/<string:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """
    根据书籍ID删除书籍
    """
    try:
        obj_id = ObjectId(book_id)
    except Exception:
        return jsonify({'error': 'Invalid book ID'}), 400

    try:
        result = collection.delete_one({'_id': obj_id})
    except errors.PyMongoError as e:
        logging.error(f"MongoDB delete error: {e}")
        return jsonify({'error': 'Failed to delete book'}), 500

    if result.deleted_count == 0:
        return jsonify({'error': 'Book not found'}), 404
    return jsonify({'message': 'Book deleted'})


@app.route('/call-price', methods=['GET'])
def call_price():
    """
    调用外部价格服务接口，默认地址和端口可通过环境变量 PRICE_SERVER 和 PRICE_PORT 设置
    支持通过 ?book_id=xxx 传参
    返回价格服务的 JSON 响应及本服务的服务器名称和IP
    """
    price_server = get_env_variable('PRICE_SERVER', 'host.docker.internal')
    price_port = get_env_variable('PRICE_PORT', '5000')

    server_name = socket.gethostname()
    try:
        server_ip = socket.gethostbyname(server_name)
    except socket.gaierror:
        server_ip = "127.0.0.1"

    book_id = request.args.get('book_id')
    price_service_url = f"http://{price_server}:{price_port}/price"
    params = {'book_id': book_id} if book_id else {}
    headers = dict(request.headers)

    try:
        response = requests.get(price_service_url, params=params, headers=headers, timeout=2)
        response.raise_for_status()
        return jsonify({
            "message": "Call price Service",
            "server_name": server_name,
            "server_ip": server_ip,
            "response from price server": response.json()
        })
    except requests.exceptions.Timeout:
        return jsonify({'message': 'Request to price service timed out'}), 504
    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling price service: {e}")
        return jsonify({'message': 'Failed to call price service', 'error': str(e)}), 500


@app.route('/healthz', methods=['GET'])
def health_check():
    """健康检查接口，返回服务状态"""
    return jsonify({"status": "ok"}), 200


def get_version() -> str:
    """读取版本号文件version.txt，如果不存在则返回 unknown"""
    try:
        with open("version.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "unknown"


if __name__ == '__main__':
    version = get_version()
    logging.info(f"Starting Book Store version: {version}")
    # 启动Flask应用，监听0.0.0.0:5000端口
    app.run(debug=True, host='0.0.0.0', port=5000)
