import logging
import certifi
import boto3
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger

from pymongo import MongoClient

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
    CORS_ORIGINS
)

# 创建 Flask app 实例
app = Flask(__name__)

# ✅ 配置 X-Ray 服务名
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

# 全局响应钩子：将 trace ID 添加到响应头
@app.after_request
def add_trace_id_header(response):
    try:
        trace_id = xray_recorder.current_segment().trace_id
        response.headers['X-Amzn-Trace-Id'] = trace_id
        response.headers['Access-Control-Expose-Headers'] = 'X-Amzn-Trace-Id'
    except Exception:
        pass
    return response

# 导入路由
from .routes_auth import *
from .routes_books import *
from .routes_misc import *
from .routes_users import *
from .routes_orders import *