import logging
import certifi
import boto3
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger

from pymongo import MongoClient

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

# 导入路由
from .routes_auth import *
from .routes_book import *
from .routes_misc import *

