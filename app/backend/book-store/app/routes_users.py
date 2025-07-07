from flask import jsonify
from flasgger import swag_from

from . import app
# from .swagger_defs import list_users_doc

# 从 app 获取 MongoDB 的 users 集合
users_collection = app.db.users

@app.route('/users', methods=['GET'])
# @swag_from(list_users_doc)
def list_users():
    """
    列出所有用户
    """
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
