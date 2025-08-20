from flask import jsonify, request
from . import app
from .prices_data import prices

@app.route('/price/<string:book_id>', methods=['GET'])
def get_price(book_id):
    # 日志记录请求信息
    app.logger.info("Request headers: %s", dict(request.headers))

    # 获取追踪头信息（OpenTelemetry 和 Zipkin）
    traceparent = request.headers.get("traceparent")
    x_b3_trace_id = request.headers.get("X-B3-TraceId")

    # 解析 traceparent 中的 trace-id（OpenTelemetry）
    changed_trace_id = None
    if traceparent:
        parts = traceparent.split("-")
        if len(parts) >= 2:
            changed_trace_id = parts[1]

    # 构建追踪信息统一结构
    trace_info = {
        "traceparent": traceparent,
        "changed_trace_id": changed_trace_id,
        "x_b3_trace_id": x_b3_trace_id
    }

    try:
        if book_id in prices:
            return jsonify({
                "book_id": book_id,
                "price": prices[book_id],
                **trace_info
            }), 200
        else:
            return jsonify({
                "error": "Price not found",
                **trace_info
            }), 404

    except Exception as e:
        app.logger.error(f"Failed to retrieve price for {book_id}: {e}")
        return jsonify({
            "error": "Failed to retrieve price",
            "details": str(e),
            **trace_info
        }), 500
