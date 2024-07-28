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


if __name__ == '__main__':
    app.run(debug=True)
