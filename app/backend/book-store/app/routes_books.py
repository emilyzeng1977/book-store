from flask import request, jsonify
from flasgger import swag_from
from bson.objectid import ObjectId
from pymongo import errors
import logging

from . import app
from .auth import token_required
from .swagger_defs import *
collection = app.collection

@app.route('/books', methods=['GET'])
@token_required(role=None)
@swag_from(books_get_doc)
def get_books():
    try:
        books = [dict(book, _id=str(book['_id'])) for book in collection.find().max_time_ms(1000)]
        return jsonify({'books': books})
    except errors.PyMongoError as e:
        logging.error(f"Error fetching books: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/books/<string:book_id>', methods=['GET'])
@token_required(role=None)
@swag_from(books_id_get_doc)
def get_book(book_id):
    try:
        book = collection.find_one({'_id': ObjectId(book_id)})
        if book:
            book['_id'] = str(book['_id'])
            return jsonify(book)
        return jsonify({'error': 'Book not found'}), 404
    except Exception:
        return jsonify({'error': 'Invalid book ID'}), 400

@app.route('/books', methods=['POST'])
@token_required(role=None)
@swag_from(books_post_doc)
def add_book():
    data = request.json
    if not data or 'title' not in data or 'author' not in data:
        return jsonify({'error': 'title and author required'}), 400
    try:
        result = collection.insert_one({'title': data['title'], 'author': data['author']})
        return jsonify({'_id': str(result.inserted_id), 'title': data['title'], 'author': data['author']}), 201
    except Exception as e:
        logging.error(f"Insert failed: {e}")
        return jsonify({'error': 'Insert failed'}), 500

@app.route('/books/<string:book_id>', methods=['PUT'])
@token_required(role=None)
def update_book(book_id):
    data = request.json or {}
    update_data = {k: v for k, v in data.items() if k in ['title', 'author'] and isinstance(v, str)}
    if not update_data:
        return jsonify({'error': 'No valid fields to update'}), 400
    try:
        result = collection.update_one({'_id': ObjectId(book_id)}, {'$set': update_data})
        if result.matched_count == 0:
            return jsonify({'error': 'Book not found'}), 404
        book = collection.find_one({'_id': ObjectId(book_id)})
        book['_id'] = str(book['_id'])
        return jsonify(book)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/books/<string:book_id>', methods=['DELETE'])
@token_required(role=None)
@swag_from(books_delete_doc)
def delete_book(book_id):
    try:
        result = collection.delete_one({'_id': ObjectId(book_id)})
        if result.deleted_count == 0:
            return jsonify({'error': 'Book not found'}), 404
        return jsonify({'message': 'Book deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
