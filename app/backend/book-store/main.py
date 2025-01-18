import logging
import os
import requests  # To make HTTP requests to other endpoints

import socket
import timeout_decorator

from bson.objectid import ObjectId
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient, errors

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)

def get_env_variable(key, default_value):
    """Get an environment variable or return the default value if it's not set or empty."""
    value = os.getenv(key)
    return value if value else default_value

# Read environment variables with robust defaults
mongo_user = get_env_variable("MONGO_USER", "tom")
mongo_password = get_env_variable("MONGO_PASSWORD", "123456")
mongo_host = get_env_variable("MONGO_HOST", "mongo")
mongo_port = int(get_env_variable("MONGO_PORT", "27017"))  # Ensure it's an integer
mongo_db = get_env_variable("MONGO_DB", "book-store")

# Construct the MongoDB URI
mongo_uri = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_db}"

try:
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=1000)
    db = client[mongo_db]  # 动态获取数据库对象
    collection = db.books
    logging.info(f"Connected to MongoDB database: {mongo_db}")
except Exception as e:
    logging.error(f"Error connecting to MongoDB: {e}")
    raise


# Greet method to return a greeting message along with the local IP
@app.route('/greet', methods=['GET'])
def greet():
    # Get the 'name' parameter from the query string, default to 'World' if not provided
    name = request.args.get('name', 'World')
    logging.info("greet, name: %s", name)

    # Retrieve the local machine's IP address
    hostname = socket.gethostname()
    # 获取服务器的 IP 地址
    try:
        local_ip = socket.gethostbyname(hostname)
    except socket.gaierror:
        local_ip = "127.0.0.1"  # 默认值

    # Create a greeting message that includes the local IP
    greeting_message = f"Hello, {name}! This server's IP address is {local_ip}."

    # Return the greeting message as a JSON response
    return jsonify({'message': greeting_message})


# Retrieve all books
@app.route('/books', methods=['GET'])
@timeout_decorator.timeout(1, use_signals=False)  # 超时设为1秒
def get_books():
    try:
        books = []
        # 设置查询超时时间
        for book in collection.find().max_time_ms(1000):  # 查询超时设置为 1 秒
            book['_id'] = str(book['_id'])
            books.append(book)
        return jsonify({'books': books})
    except errors.ExecutionTimeout:
        return jsonify({'error': 'Query timed out'}), 504
    except errors.PyMongoError as e:
        return jsonify({'error': str(e)}), 500


# Retrieve a single book by ID
@app.route('/books/<string:book_id>', methods=['GET'])
def get_book(book_id):
    book = collection.find_one({'_id': ObjectId(book_id)})
    if book:
        book['_id'] = str(book['_id'])
        return jsonify(book)
    return jsonify({'error': 'Book not found'}), 404


# Add a new book
@app.route('/books', methods=['POST'])
def add_book():
    if not request.json or not 'title' in request.json or not 'author' in request.json:
        return jsonify({'error': 'The new book must have a title and author'}), 400

    new_book = {
        'title': request.json['title'],
        'author': request.json['author']
    }
    result = collection.insert_one(new_book)
    new_book['_id'] = str(result.inserted_id)
    return jsonify(new_book), 201


# Update a book by ID
@app.route('/books/<string:book_id>', methods=['PUT'])
def update_book(book_id):
    if not request.json:
        return jsonify({'error': 'Invalid request'}), 400

    update_data = {}
    if 'title' in request.json:
        if not isinstance(request.json['title'], str):
            return jsonify({'error': 'Invalid title'}), 400
        update_data['title'] = request.json['title']

    if 'author' in request.json:
        if not isinstance(request.json['author'], str):
            return jsonify({'error': 'Invalid author'}), 400
        update_data['author'] = request.json['author']

    result = collection.update_one(
        {'_id': ObjectId(book_id)},
        {'set': update_data}
    )

    if result.matched_count == 0:
        return jsonify({'error': 'Book not found'}), 404

    book = collection.find_one({'_id': ObjectId(book_id)})
    book['_id'] = str(book['_id'])
    return jsonify(book)


# Delete a book by ID
@app.route('/books/<string:book_id>', methods=['DELETE'])
def delete_book(book_id):
    result = collection.delete_one({'_id': ObjectId(book_id)})
    if result.deleted_count == 0:
        return jsonify({'error': 'Book not found'}), 404
    return jsonify({'message': 'Book deleted'})

# New endpoint to call price for a book from another service
@app.route('/call-price', methods=['GET'])
@timeout_decorator.timeout(2, use_signals=False)  # 超时设为1秒
def call_price():
    # 读取环境变量
    price_server = get_env_variable('PRICE_SERVER', 'host.docker.internal')
    price_port = get_env_variable('PRICE_PORT', '5000')

    # 获取服务器的主机名
    server_name = socket.gethostname()

    # 获取服务器的 IP 地址
    try:
        server_ip = socket.gethostbyname(server_name)
    except socket.gaierror:
        server_ip = "127.0.0.1"  # 默认值

    # 获取 book_id 参数
    book_id = request.args.get('book_id')  # 如果未提供 book_id，则返回 None

    # 构造 price 服务的 URL
    price_service_url = f"http://{price_server}:{price_port}/price"
    params = {'book_id': book_id} if book_id else {}  # 仅在 book_id 存在时添加参数

    try:
        # 发起 HTTP 请求
        response = requests.get(price_service_url, params=params, timeout=1)
        response.raise_for_status()  # 检查响应状态码

        # 创建返回的 Flask 响应
        # 创建返回的 Flask 响应
        flask_response = jsonify({
            "message": "Call price Service",
            "server_name": server_name,
            "server_ip": server_ip,
            "response from price server": response.json()
        })

        # 如果响应中包含 traceparent，将其加入到当前响应的 headers
        traceparent = response.headers.get('traceparent')
        if traceparent:
            flask_response.headers['traceparent'] = traceparent

        return flask_response

    except requests.exceptions.Timeout:
        flask_response = jsonify({'message': 'Request to price service timed out'})
        flask_response.headers.update(request.headers)
        return flask_response, 504

    except requests.exceptions.RequestException as e:
        flask_response = jsonify({'message': 'Failed to call price service', 'error': str(e)})
        flask_response.headers.update(request.headers)
        return flask_response, 500


@app.route('/healthz', methods=['GET'])
def health_check():
    # 这里可以添加你想要的健康检查逻辑
    # 例如，检查数据库连接或其他依赖服务是否可用
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
