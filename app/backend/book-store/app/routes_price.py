from flask import jsonify, request
from . import app
from .prices_data import prices

@app.route('/price/<string:book_id>', methods=['GET'])
def get_price(book_id):
    # 日志记录请求信息
    app.logger.info("Request headers: %s", dict(request.headers))
    try:
        if book_id in prices:
            return jsonify({
                "book_id": book_id,
                "price": prices[book_id]
            }), 200
        else:
            return jsonify({
                "error": "Price not found"
            }), 404

    except Exception as e:
        app.logger.error(f"Failed to retrieve price for {book_id}: {e}")
        return jsonify({
            "error": "Failed to retrieve price",
            "details": str(e)
        }), 500
