from flask import jsonify, g
from flasgger import swag_from

from . import app
from .auth import token_required
from .swagger_defs import *

# 从 app 获取 MongoDB 的 users 集合
users_collection = app.db.users

@app.route('/users', methods=['GET'])
@token_required(role=['admin'])
@swag_from(users_list_doc)
def list_users():
    try:
        users = users_collection.find()
        result = []
        for user in users:
            result.append({
                "username": user.get("username"),
                "role": user.get("role"),
                "created_at": user.get("created_at").isoformat() if user.get("created_at") else None
            })
        return jsonify(result), 200
    except Exception as e:
        app.logger.error(f"Failed to retrieve users: {e}")
        return jsonify({"error": "Failed to retrieve users", "details": str(e)}), 500

@app.route('/users/current', methods=['GET'])
@token_required(role=None)
@swag_from(users_current_doc)
def get_current_user():
    try:
        user = g.get("user")
        if not user:
            return jsonify({"error": "User not found"}), 403

        result = {
            "username": user.get("username"),
            "role": user.get("role"),
            "created_at": user.get("created_at").isoformat() if user.get("created_at") else None
        }
        return jsonify(result), 200
    except Exception as e:
        app.logger.error(f"Failed to retrieve current user: {e}")
        return jsonify({"error": "Failed to retrieve current user", "details": str(e)}), 500
