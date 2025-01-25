import logging
import os
import socket
from time import time

from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)
CORS(app)

def get_env_variable(key, default_value):
    """Get an environment variable or return the default value if it's not set or empty."""
    value = os.getenv(key)
    return value if value else default_value

# 获取 OpenTelemetry Collector 的 URL
otel_collector_url = get_env_variable("OTEL_COLLECTOR_URL", "grpc://opentelemetry-collector.default.svc.cluster.local:4317")

# 设置 OpenTelemetry 配置，指定服务名称
service_name = "monitor-demo"
resource = Resource.create({SERVICE_NAME: service_name})

# 创建 TracerProvider，并指定 Resource（服务名称）
trace.set_tracer_provider(TracerProvider(resource=resource))

# 获取 Tracer
tracer = trace.get_tracer(__name__)

# 配置 OTLP 导出器
otlp_exporter = OTLPSpanExporter(endpoint=otel_collector_url, insecure=True)

# 配置 SpanProcessor 并添加到 TracerProvider
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# 配置 Prometheus 导出器
reader = PrometheusMetricReader()
provider = MeterProvider(metric_readers=[reader])
metrics.set_meter_provider(provider)

# 自动化 Flask 监控
FlaskInstrumentor().instrument_app(app)

logging.basicConfig(level=logging.INFO)

# 定义请求时长指标
meter = metrics.get_meter(__name__)
request_counter = meter.create_counter(
    "http_requests_total",
    description="Total number of HTTP requests",
)

# 添加中间件来记录请求时长，并跟踪活跃请求数
@app.before_request
def before_request():
    request.start_time = time()

@app.after_request
def after_request(response):
    if request.path != "/metrics":  # 排除 /metrics 自身的统计
        method = request.method
        status = response.status_code
        url = request.path
        # 记录请求总数到 Prometheus
        request_counter.add(1, {"method": method, "status": str(status), "url": url})
        logging.info(f"Request to {url} with method {method} resulted in status {status}")
    return response

# 暴露 Prometheus 指标的端点
@app.route('/metrics', methods=['GET'])
def metrics_endpoint():
    # Extract all lines related to http_requests_total
    all_metrics = generate_latest().decode('utf-8')
    filtered_metrics = []

    for line in all_metrics.splitlines():
        if line.startswith("# HELP http_requests_total") or \
                line.startswith("# TYPE http_requests_total") or \
                line.startswith("http_requests_total"):
            filtered_metrics.append(line)

    # Join the filtered lines to create the output
    metrics_data = "\n".join(filtered_metrics)

    # Return the filtered metrics
    return metrics_data, 200, {'Content-Type': 'text/plain; charset=utf-8'}


# Greet method to return a greeting message along with the local IP
@app.route('/greet', methods=['GET'])
def greet():
    # Get the 'name' parameter from the query string, default to 'World' if not provided
    name = request.args.get('name', 'World')
    logging.info("greet, name: %s", name)

    # If name is "error" or "err", return HTTP 500
    if name.lower() in ["error", "err"]:
        logging.error("Simulated server error for name: %s", name)
        return jsonify({"error": "Simulated server error"}), 500

    # Retrieve the local machine's IP address
    hostname = socket.gethostname()
    # 获取服务器的 IP 地址
    try:
        local_ip = socket.gethostbyname(hostname)
    except socket.gaierror:
        local_ip = "127.0.0.1"  # 默认值

    # Create a greeting message that includes the local IP
    greeting_message = f"Hello, {name}! This server's IP address is {local_ip}."

    # Get the current active span and its trace ID
    current_span = trace.get_current_span()
    trace_id = current_span.get_span_context().trace_id

    # Convert trace ID to a hex string
    trace_id_hex = f"{trace_id:032x}"

    # Create a JSON response and add the Trace ID to the headers
    response = make_response(jsonify({'message': greeting_message}))
    response.headers['X-Trace-Id'] = trace_id_hex

    return response

@app.route('/test', methods=['POST'])
def test_post():
    """Handle POST requests to /test."""
    try:
        # 从请求中获取 JSON 数据
        data = request.get_json()
        logging.info("Received data: %s", data)

        # 简单逻辑：将数据中的 key-value 转换为大写（示例处理）
        processed_data = {k.upper(): v.upper() if isinstance(v, str) else v for k, v in data.items()}

        # 返回处理后的数据
        response = {
            "message": "Data processed successfully",
            "processed_data": processed_data
        }
        return jsonify(response), 200

    except Exception as e:
        logging.error("Error in /test: %s", str(e))
        return jsonify({"error": "Invalid request", "message": str(e)}), 400


@app.route('/healthz', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
