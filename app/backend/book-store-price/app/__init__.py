import logging
from flask import Flask


# 创建 Flask app 实例
app = Flask(__name__)

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

# 导入路由
from .routes_price import *
from .routes_misc import *
