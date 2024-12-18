# import logging
import os
import requests  # To make HTTP requests to other endpoints

import socket

from bson.objectid import ObjectId
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# logging.basicConfig(level=logging.INFO)

# Read environment variables with default values
mongo_user = os.getenv("MONGO_USER", "tom")
mongo_password = os.getenv("MONGO_PASSWORD", "123456")
mongo_host = os.getenv("MONGO_HOST", "localhost")
mongo_port = os.getenv("MONGO_PORT", "27017")
mongo_db = os.getenv("MONGO_DB", "book_store")

# Construct the MongoDB URI
mongo_uri = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_db}"

try:
    client = MongoClient(mongo_uri)
    db = client.book_store
    collection = db.books
    # logging.info("Connected to MongoDB")
except Exception as e:
    # logging.error(f"Error connecting to MongoDB: {e}")
    raise


# Greet method to return a greeting message along with the local IP
@app.route('/greet', methods=['GET'])
def greet():
    # Get the 'name' parameter from the query string, default to 'World' if not provided
    name = request.args.get('name', 'World')

    # Retrieve the local machine's IP address
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    # Create a greeting message that includes the local IP
    greeting_message = f"Hello, {name}! This server's IP address is {local_ip}."

    # Return the greeting message as a JSON response
    return jsonify({'message': greeting_message})


# Retrieve all books
@app.route('/books', methods=['GET'])
def get_books():
    books = []
    for book in collection.find():
        book['_id'] = str(book['_id'])
        books.append(book)
    return jsonify({'books': books})


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

# New endpoint to call /hello from another service
@app.route('/call-hello', methods=['GET'])
def call_hello():
    # 读取环境变量
    hello_server = os.getenv('HELLO_SERVER', 'host.docker.internal')
    hello_port = os.getenv('HELLO_PORT', '5000')

    # hello_path
    hello_path = request.args.get('hello_path') or 'hello'

    # 获取服务器的主机名
    server_name = socket.gethostname()

    # 获取服务器的 IP 地址
    try:
        server_ip = socket.gethostbyname(server_name)
    except socket.gaierror:
        server_ip = "127.0.0.1"  # 默认值

    # 获取查询参数
    error_host_name = request.args.get('error_host_name')

    # 构造 hello 服务的 URL
    hello_service_url = f"http://{hello_server}:{hello_port}/{hello_path}"
    if error_host_name:
        hello_service_url += f"?error_host_name={error_host_name}"

    try:
        # 发起 HTTP 请求
        response = requests.get(hello_service_url, timeout=5)
        response.raise_for_status()  # 检查响应状态码

        # 创建返回的 Flask 响应
        # 创建返回的 Flask 响应
        flask_response = jsonify({
            "message": "Called Hello Service",
            "server_name": server_name,
            "server_ip": server_ip,
            "response from hello server": response.json()
        })

        # 如果响应中包含 traceparent，将其加入到当前响应的 headers
        traceparent = response.headers.get('traceparent')
        if traceparent:
            flask_response.headers['traceparent'] = traceparent

        return flask_response

    except requests.exceptions.Timeout:
        flask_response = jsonify({'message': 'Request to hello service timed out'})
        flask_response.headers.update(request.headers)
        return flask_response, 504

    except requests.exceptions.RequestException as e:
        flask_response = jsonify({'message': 'Failed to call hello service', 'error': str(e)})
        flask_response.headers.update(request.headers)
        return flask_response, 500


@app.route('/healthz', methods=['GET'])
def health_check():
    # 这里可以添加你想要的健康检查逻辑
    # 例如，检查数据库连接或其他依赖服务是否可用
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
