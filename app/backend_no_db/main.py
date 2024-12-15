import os
import requests  # To make HTTP requests to other endpoints

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 初始书籍数据
books = [
    {'id': 1, 'title': '1984', 'author': 'George Orwell'},
    {'id': 2, 'title': 'To Kill a Mockingbird', 'author': 'Harper Lee'},
    {'id': 3, 'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald'}
]

@app.route('/greet', methods=['GET'])
def greet():

    # 将请求头添加到响应头
    response = jsonify({'message': 'hello world'})
    for header, value in request.headers.items():
        response.headers[header] = value

    # 返回包含问候信息的 JSON 响应
    return response

# Retrieve all books, with optional filtering by author
@app.route('/books', methods=['GET'])
def get_books():
    author = request.args.get('author')
    if author:
        filtered_books = [book for book in books if book['author'] == author]
        if filtered_books:
            return jsonify({'books': filtered_books})
        else:
            return jsonify({'message': f'No books found for author: {author}'}), 404
    return jsonify({'books': books})


# 根据 ID 获取单本书
@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((book for book in books if book['id'] == book_id), None)
    if book is not None:
        return jsonify(book)
    else:
        return jsonify({'message': 'Book not found'}), 404


# 添加新书
@app.route('/books', methods=['POST'])
def add_book():
    new_book = request.get_json()
    new_book['id'] = books[-1]['id'] + 1 if books else 1
    books.append(new_book)
    return jsonify(new_book), 201


# 更新书籍信息
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    updated_book = request.get_json()
    book = next((book for book in books if book['id'] == book_id), None)
    if book is not None:
        book.update(updated_book)
        return jsonify(book)
    else:
        return jsonify({'message': 'Book not found'}), 404


# 删除书籍
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    global books
    books = [book for book in books if book['id'] != book_id]
    return jsonify({'message': 'Book deleted'})

# New endpoint to call /hello from another service
@app.route('/call-hello', methods=['GET'])
def call_hello():
    # 读取环境变量
    hello_server = os.getenv('HELLO_SERVER', 'host.docker.internal')
    hello_port = os.getenv('HELLO_PORT', '5000')
    hello_uri = os.getenv('HELLO_URI', 'hello')

    # 获取查询参数
    error_host_name = request.args.get('error_host_name')

    # 构造 hello 服务的 URL
    hello_service_url = f"http://{hello_server}:{hello_port}/{hello_uri}"
    if error_host_name:
        hello_service_url += f"?error_host_name={error_host_name}"

    try:
        # 发起 HTTP 请求
        response = requests.get(hello_service_url, timeout=5)
        response.raise_for_status()  # 检查响应状态码

        # 构造响应对象并附加请求头
        flask_response = jsonify({'message': 'Hello service response', 'data': response.json()})
        flask_response.headers.update(request.headers)
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
