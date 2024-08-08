from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import logging, os

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.DEBUG)

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
    logging.info("Connected to MongoDB")
except Exception as e:
    logging.error(f"Error connecting to MongoDB: {e}")
    raise


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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
