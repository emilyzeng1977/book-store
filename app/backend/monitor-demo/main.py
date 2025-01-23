import logging
import os
import socket

from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

app = Flask(__name__)
CORS(app)

def get_env_variable(key, default_value):
    """Get an environment variable or return the default value if it's not set or empty."""
    value = os.getenv(key)
    return value if value else default_value

otel_coolector_url = get_env_variable("OTEL_COLLECTOR_URL", "grpc://opentelemetry-collector.default.svc.cluster.local:4317")

# 设置 OpenTelemetry 配置，指定服务名称
service_name = "monitor-demo"
resource = Resource.create({SERVICE_NAME: service_name})

# 创建 TracerProvider，并指定 Resource（服务名称）
trace.set_tracer_provider(TracerProvider(resource=resource))

# 获取 Tracer
tracer = trace.get_tracer(__name__)

# 配置 OTLP 导出器
otlp_exporter = OTLPSpanExporter(endpoint=otel_coolector_url, insecure=True)

# 配置 SpanProcessor 并添加到 TracerProvider
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# 自动化 Flask 监控
FlaskInstrumentor().instrument_app(app)

logging.basicConfig(level=logging.INFO)

# Greet method to return a greeting message along with the local IP
@app.route('/greet', methods=['GET'])
def greet():
    # Get the 'name' parameter from the query string, default to 'World' if not provided
    name = request.args.get('name', 'World')
    logging.info("greet, name: %s", name)

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

@app.route('/healthz', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
