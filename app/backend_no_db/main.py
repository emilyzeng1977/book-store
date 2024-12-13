import socket
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
    hello_server = os.getenv('HELLO_SERVER', 'hello')
    hello_port = os.getenv('HELLO_PORT', '5000')
    hello_uri = os.getenv('HELLO_URI', 'hello')

    # 获取请求中的 error_host_name 参数
    error_host_name = request.args.get('error_host_name')

    # 构造 hello 服务的 URL，只有当 error_host_name 不为空时才附加该参数
    hello_service_url = f'http://{hello_server}:{hello_port}/{hello_uri}'
    if error_host_name:
        hello_service_url += f'?error_host_name={error_host_name}'

    try:
        response = requests.get(hello_service_url)
        response.raise_for_status()
        return jsonify({'message': 'Hello service response', 'data': response.json()})
    except requests.exceptions.RequestException as e:
        return jsonify({'message': 'Failed to call hello service', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
