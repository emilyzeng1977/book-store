import logging
from flask import Flask

# ✅ X-Ray 相关导入
from aws_xray_sdk.core import xray_recorder, patch_all
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware

# 创建 Flask app 实例
app = Flask(__name__)

# ✅ 配置 X-Ray 服务名
xray_recorder.configure(service='book-store-price')
XRayMiddleware(app, xray_recorder)

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

# 导入路由
from .routes_price import *
from .routes_misc import *
