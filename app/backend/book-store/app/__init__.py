import logging
import certifi
import boto3
from flask import Flask, request, g
from flask_cors import CORS
from flasgger import Swagger
from pymongo import MongoClient

import time
import json
from datetime import datetime

# ✅ X-Ray 相关导入
from aws_xray_sdk.core import xray_recorder, patch
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware

from .config import (
    ATLAS_MONGO_USER,
    ATLAS_MONGO_PASSWORD,
    ATLAS_MONGO_HOST,
    ATLAS_MONGO_APP_NAME,
    ATLAS_MONGO_DB,
    AWS_REGION,
    CORS_ORIGINS,
    AWS_XRAY_ENABLE
)

# 创建 Flask app 实例
app = Flask(__name__)

# ✅ 配置 X-Ray 服务名
if AWS_XRAY_ENABLE:
    xray_recorder.configure(service='book-store')
    patch(['requests'])
    XRayMiddleware(app, xray_recorder)

# 配置 Swagger UI 安全定义
app.config['SWAGGER'] = {
    'title': 'Bookstore API',
    'uiversion': 3,
    'securityDefinitions': {
        'BearerAuth': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    }
}

swagger = Swagger(app)

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

cors_origins = [origin.strip() for origin in CORS_ORIGINS.split(',') if origin.strip()]
CORS(app,
     supports_credentials=True,
     origins=cors_origins)

# 初始化 AWS Cognito client
cognito_client = boto3.client('cognito-idp', region_name=AWS_REGION)

# 初始化 MongoDB 连接
atlas_mongo_uri = (
    f"mongodb+srv://{ATLAS_MONGO_USER}:{ATLAS_MONGO_PASSWORD}@{ATLAS_MONGO_HOST}"
    f"/?retryWrites=true&w=majority&appName={ATLAS_MONGO_APP_NAME}"
)

try:
    client = MongoClient(atlas_mongo_uri, serverSelectionTimeoutMS=3000, tlsCAFile=certifi.where())
    db = client[ATLAS_MONGO_DB]
    collection = db.books
    logging.info(f"Connected to MongoDB database: {ATLAS_MONGO_DB}")
    print(client.list_database_names())
except Exception as e:
    logging.error(f"Error connecting to MongoDB: {e}")
    raise

# 将上面创建的资源附加到 app 对象上，方便其他模块调用
app.cognito_client = cognito_client
app.db = db
app.collection = collection


# 设置 logger
logger = logging.getLogger("request_response_logger")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()  # 可换成 FileHandler
handler.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(handler)
logger.propagate = False   # ⬅️ 加上这行，避免重复打印

@app.before_request
def start_timer():
    g.start_time = time.time()

@app.after_request
def log_request_response_trace_id(response):
    try:
        duration = round(time.time() - g.start_time, 4)

        # 可选：AWS X-Ray trace ID
        trace_id = None
        if AWS_XRAY_ENABLE:
            trace_id = None
            segment = xray_recorder.current_segment()
            if segment:
                trace_id = segment.trace_id
                response.headers['X-Amzn-Trace-Id'] = trace_id
                response.headers['Access-Control-Expose-Headers'] = 'X-Amzn-Trace-Id'

        # 请在这里写request和response日志
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "remote_addr": request.remote_addr,
            "method": request.method,
            "url": request.url,
            "request_headers": dict(request.headers),
            "query_params": request.args.to_dict(),
            "request_body": get_request_body(),
            "http.statusCode": response.status_code,  # 使用标准字段名便于 New Relic 识别
            "response_headers": dict(response.headers),
            "response_body": get_response_body(response),
            "duration": duration
        }
        logger.info(json.dumps(log_data))

    except Exception:
        pass
    return response

# 辅助函数：安全读取请求体
def get_request_body():
    try:
        if request.is_json:
            return request.get_json()
        return request.get_data(as_text=True)
    except Exception:
        return "<unreadable>"

# 辅助函数：读取响应体
def get_response_body(response):
    try:
        return response.get_data(as_text=True)
    except Exception:
        return "<unreadable>"

# 导入路由
from .routes_auth import *
from .routes_books import *
from .routes_misc import *
from .routes_users import *
from .routes_orders import *