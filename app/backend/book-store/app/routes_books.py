from flask import request, jsonify
from flasgger import swag_from
from pymongo import errors
import logging

from . import app
from .auth import token_required
from .swagger_books_defs import *

collection = app.collection

def serialize_book(book):
    if '_id' in book:
        book['_id'] = str(book['_id'])
    return book

@app.route('/books', methods=['GET'])
@token_required(role=None)
@swag_from(books_get_doc)
def get_books():
    try:
        books = []
        for book in collection.find().max_time_ms(1000):
            books.append({
                'book_id': book.get('book_id'),
                'title': book.get('title', ''),
                'author': book.get('author', ''),
                'description': book.get('description', '')
            })
        return jsonify({'books': books})
    except errors.PyMongoError as e:
        logging.error(f"Error fetching books: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/books/<string:book_id>', methods=['GET'])
@token_required(role=None)
@swag_from(books_id_get_doc)
def get_book(book_id):
    try:
        book = collection.find_one({'book_id': book_id})
        if book:
            return jsonify(serialize_book(book))
        return jsonify({'error': 'Book not found'}), 404
    except Exception:
        return jsonify({'error': 'Invalid book ID'}), 400

@app.route('/books', methods=['POST'])
@token_required(role=['admin'])
@swag_from(books_post_doc)
def add_book():
    data = request.json
    if not data or 'title' not in data or 'author' not in data:
        return jsonify({'error': 'title and author required'}), 400

    try:
        # 自动生成 book_id，例如 BK000011
        last_book = collection.find().sort('book_id', -1).limit(1)
        last_id = list(last_book)[0]['book_id'] if last_book.count() > 0 else 'BK000000'
        next_id = f"BK{int(last_id[2:]) + 1:06d}"

        book_data = {
            'book_id': next_id,
            'title': data['title'],
            'author': data['author'],
            'description': data.get('description', '')
        }

        collection.insert_one(book_data)
        return jsonify(book_data), 201

    except Exception as e:
        logging.error(f"Insert failed: {e}")
        return jsonify({'error': 'Insert failed'}), 500


@app.route('/books/<string:book_id>', methods=['PUT'])
@token_required(role=['admin'])
def update_book(book_id):
    data = request.json or {}

    # 只允许更新 title、author、description 且必须是字符串
    allowed_fields = ['title', 'author', 'description']
    update_data = {k: v for k, v in data.items() if k in allowed_fields and isinstance(v, str)}

    if not update_data:
        return jsonify({'error': 'No valid fields to update'}), 400

    try:
        result = collection.update_one({'book_id': book_id}, {'$set': update_data})
        if result.matched_count == 0:
            return jsonify({'error': 'Book not found'}), 404

        book = collection.find_one({'book_id': book_id})
        return jsonify(serialize_book(book))

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/books/<string:book_id>', methods=['DELETE'])
@token_required(role=['admin'])
@swag_from(books_delete_doc)
def delete_book(book_id):
    try:
        result = collection.delete_one({'book_id': book_id})
        if result.deleted_count == 0:
            return jsonify({'error': 'Book not found'}), 404
        return jsonify({'message': 'Book deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
