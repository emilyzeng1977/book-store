from flask import request, jsonify, g
from datetime import datetime
from flasgger import swag_from

from . import app
from .auth import token_required
from .swagger_orders_defs import (
    orders_get_all_doc,
    orders_get_my_doc,
    orders_create_doc,
    orders_delete_doc
)
from .utils import serialize_book

orders_collection = app.db.orders

@app.route('/orders', methods=['GET'])
@token_required(role=['admin'])
@swag_from(orders_get_all_doc)
def get_all_orders():
    try:
        orders = list(orders_collection.find())
        result = []
        for order in orders:
            result.append({
                "username": order.get("username"),
                "book_id": order.get("book_id"),
                "created_at": order.get("created_at").isoformat() if order.get("created_at") else None
            })
        return jsonify(result), 200
    except Exception as e:
        app.logger.error(f"Failed to retrieve orders: {e}")
        return jsonify({"error": "Failed to retrieve orders", "details": str(e)}), 500

@app.route('/orders/my', methods=['GET'])
@token_required(role=None)
@swag_from(orders_get_my_doc)
def get_my_orders():
    try:
        username = g.user.get("username")
        orders = orders_collection.find({"username": username})
        result = []
        for order in orders:
            result.append({
                "book_id": order.get("book_id"),
                "created_at": order.get("created_at").isoformat() if order.get("created_at") else None
            })
        return jsonify(result), 200
    except Exception as e:
        app.logger.error(f"Failed to retrieve user orders: {e}")
        return jsonify({"error": "Failed to retrieve orders", "details": str(e)}), 500

@app.route('/orders', methods=['POST'])
@token_required(role='user')
@swag_from(orders_create_doc)
def create_order():
    try:
        username = g.user.get("username")
        data = request.json
        book_id = data.get("book_id")

        if not book_id:
            return jsonify({"error": "book_id is required"}), 400

        existing = orders_collection.find_one({"username": username, "book_id": book_id})
        if existing:
            return jsonify({"error": "Order already exists"}), 400

        order = {
            "username": username,
            "book_id": book_id,
            "created_at": datetime.utcnow()
        }

        orders_collection.insert_one(order)
        return jsonify(serialize_book(order)), 201
    except Exception as e:
        app.logger.error(f"Failed to create order: {e}")
        return jsonify({"error": "Failed to create order", "details": str(e)}), 500

@app.route('/orders/<string:book_id>', methods=['DELETE'])
@token_required(role=['user'])
@swag_from(orders_delete_doc)
def delete_order(book_id):
    try:
        username = g.user.get("username")
        result = orders_collection.delete_one({"username": username, "book_id": book_id})
        if result.deleted_count == 0:
            return jsonify({"error": "Order not found"}), 404
        return jsonify({"message": "Order deleted"}), 200
    except Exception as e:
        app.logger.error(f"Failed to delete order: {e}")
        return jsonify({"error": "Failed to delete order", "details": str(e)}), 500
