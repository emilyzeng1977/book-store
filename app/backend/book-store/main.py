import logging
import socket

import certifi
import requests
import boto3
from bson.objectid import ObjectId
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from flasgger import Swagger, swag_from
from pymongo import MongoClient, errors
from botocore.exceptions import ClientError

# 自定义模块导入
from auth import token_required, get_secret_hash

# swagger
from swagger_defs import auth_login_doc
from swagger_defs import books_get_doc
from swagger_defs import books_id_get_doc
from swagger_defs import books_post_doc
from swagger_defs import books_delete_doc

from config import (
    ATLAS_MONGO_USER,
    ATLAS_MONGO_PASSWORD,
    ATLAS_MONGO_HOST,
    ATLAS_MONGO_APP_NAME,
    ATLAS_MONGO_DB,
    AWS_REGION,
    COGNITO_USER_POOL_ID,
    COGNITO_CLIENT_ID,
    COOKIE_HTTPONLY,
    COOKIE_SECURE,
    COOKIE_SAMESITE,
    COOKIE_DOMAIN,
    COOKIE_MAX_AGE,
    CORS_ORIGINS_LIST,
    PRICE_PORT,
    PRICE_SERVER
)

# Flask 应用初始化
app = Flask(__name__)

swagger = Swagger(app)

# 日志配置，INFO级别，方便查看运行信息
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

cors_origins = [origin.strip() for origin in CORS_ORIGINS_LIST.split(',') if origin.strip()]
CORS(app,
     supports_credentials=True,
     origins=cors_origins) # # 需要完整指定端口

cognito_client = boto3.client('cognito-idp', region_name=AWS_REGION)

# 生成 MongoDB 连接字符串
atlas_mongo_uri = (
    f"mongodb+srv://{ATLAS_MONGO_USER}:{ATLAS_MONGO_PASSWORD}@{ATLAS_MONGO_HOST}"
    f"/?retryWrites=true&w=majority&appName={ATLAS_MONGO_APP_NAME}"
)

# 初始化 MongoDB 连接
try:
    client = MongoClient(atlas_mongo_uri, serverSelectionTimeoutMS=3000, tlsCAFile=certifi.where())  # 3秒连接超时
    db = client[ATLAS_MONGO_DB]
    collection = db.books
    logging.info(f"Connected to MongoDB database: {ATLAS_MONGO_DB}")
    print(client.list_database_names())
except Exception as e:
    logging.error(f"Error connecting to MongoDB: {e}")
    raise

# ----------------------
# 路由定义
# ----------------------
@app.route('/auth/login', methods=['POST'])
@swag_from(auth_login_doc)
def login():
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'username and password required'}), 400

    username = data['username']
    password = data['password']

    try:
        resp = cognito_client.admin_initiate_auth(
            UserPoolId=COGNITO_USER_POOL_ID,
            ClientId=COGNITO_CLIENT_ID,
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password,
                'SECRET_HASH': get_secret_hash(username)
            }
        )
        auth_result = resp['AuthenticationResult']
        access_token = auth_result['AccessToken']

        response = make_response(jsonify(auth_result))

        # 设置cookie
        response.set_cookie(
            'Authorization',
            f'Bearer {access_token}',
            httponly=COOKIE_HTTPONLY, # True: JS 不能读取，防止XSS
            secure=COOKIE_SECURE,     # 本地测试用 False, 生产环境请改成 True (只会在 HTTPS 请求中被浏览器接收或发送) ,当samesite为None时必须为True
            samesite=COOKIE_SAMESITE, # Lax|CSRF防护，可根据需求改为 'Strict', 注意，为None时候必须要HTTPS
            domain=COOKIE_DOMAIN,     # 关键点！支持跨子域共享 cookie
            max_age=COOKIE_MAX_AGE    # token有效期，比如1小时
        )
        return response

        # return jsonify(resp['AuthenticationResult'])
    except ClientError as e:
        # 返回Cognito错误信息给客户端
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        return jsonify({'error': error_code, 'message': error_message}), 401

@app.route('/greet', methods=['GET'])
def greet():
    """
    简单的问候接口，返回传入的名字和服务器IP
    示例: /greet?name=Tom
    """
    name = request.args.get('name', 'World')
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except socket.gaierror:
        local_ip = "127.0.0.1"

    greeting_message = f"Hello, {name}! This server's IP address is {local_ip} 2."
    return jsonify({'message': greeting_message})

@app.route('/books', methods=['GET'])
@token_required
@swag_from(books_get_doc)
def get_books():
    try:
        books = []
        for book in collection.find().max_time_ms(1000):
            book['_id'] = str(book['_id'])
            books.append(book)
        return jsonify({'books': books})
    except errors.ExecutionTimeout:
        return jsonify({'error': 'Query timed out'}), 504
    except errors.PyMongoError as e:
        logging.error(f"MongoDB query error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/books/<string:book_id>', methods=['GET'])
@token_required
@swag_from(books_id_get_doc)
def get_book(book_id):
    try:
        obj_id = ObjectId(book_id)
    except Exception:
        return jsonify({'error': 'Invalid book ID'}), 400

    book = collection.find_one({'_id': obj_id})
    if book:
        book['_id'] = str(book['_id'])
        return jsonify(book)
    return jsonify({'error': 'Book not found'}), 404


@app.route('/books', methods=['POST'])
@token_required
@swag_from(books_post_doc)
def add_book():
    """
    添加一本新书，要求传入 JSON，必须包含title和author字段
    """
    if not request.json or 'title' not in request.json or 'author' not in request.json:
        return jsonify({'error': 'The new book must have a title and author'}), 400

    new_book = {
        'title': request.json['title'],
        'author': request.json['author']
    }
    try:
        result = collection.insert_one(new_book)
    except errors.PyMongoError as e:
        logging.error(f"MongoDB insert error: {e}")
        return jsonify({'error': 'Failed to add book'}), 500

    new_book['_id'] = str(result.inserted_id)
    return jsonify(new_book), 201


@app.route('/books/<string:book_id>', methods=['PUT'])
@token_required
def update_book(book_id):
    """
    根据书籍ID更新书籍信息，支持title和author字段更新
    """
    try:
        obj_id = ObjectId(book_id)
    except Exception:
        return jsonify({'error': 'Invalid book ID'}), 400

    if not request.json:
        return jsonify({'error': 'Invalid request, JSON body required'}), 400

    update_data = {}
    if 'title' in request.json:
        if not isinstance(request.json['title'], str):
            return jsonify({'error': 'Invalid title'}), 400
        update_data['title'] = request.json['title']

    if 'author' in request.json:
        if not isinstance(request.json['author'], str):
            return jsonify({'error': 'Invalid author'}), 400
        update_data['author'] = request.json['author']

    if not update_data:
        return jsonify({'error': 'No valid fields to update'}), 400

    try:
        result = collection.update_one({'_id': obj_id}, {'$set': update_data})
    except errors.PyMongoError as e:
        logging.error(f"MongoDB update error: {e}")
        return jsonify({'error': 'Failed to update book'}), 500

    if result.matched_count == 0:
        return jsonify({'error': 'Book not found'}), 404

    book = collection.find_one({'_id': obj_id})
    book['_id'] = str(book['_id'])
    return jsonify(book)


@app.route('/books/<string:book_id>', methods=['DELETE'])
@token_required
@swag_from(books_delete_doc)
def delete_book(book_id):
    """
    根据书籍ID删除书籍
    """
    try:
        obj_id = ObjectId(book_id)
    except Exception:
        return jsonify({'error': 'Invalid book ID'}), 400

    try:
        result = collection.delete_one({'_id': obj_id})
    except errors.PyMongoError as e:
        logging.error(f"MongoDB delete error: {e}")
        return jsonify({'error': 'Failed to delete book'}), 500

    if result.deleted_count == 0:
        return jsonify({'error': 'Book not found'}), 404
    return jsonify({'message': 'Book deleted'})


@app.route('/call-price', methods=['GET'])
def call_price():
    """
    调用外部价格服务接口，默认地址和端口可通过环境变量 PRICE_SERVER 和 PRICE_PORT 设置
    支持通过 ?book_id=xxx 传参
    返回价格服务的 JSON 响应及本服务的服务器名称和IP
    """

    server_name = socket.gethostname()
    try:
        server_ip = socket.gethostbyname(server_name)
    except socket.gaierror:
        server_ip = "127.0.0.1"

    book_id = request.args.get('book_id')
    price_service_url = f"http://{PRICE_SERVER}:{PRICE_PORT}/price"
    params = {'book_id': book_id} if book_id else {}
    headers = dict(request.headers)

    try:
        response = requests.get(price_service_url, params=params, headers=headers, timeout=2)
        response.raise_for_status()
        return jsonify({
            "message": "Call price Service",
            "server_name": server_name,
            "server_ip": server_ip,
            "response from price server": response.json()
        })
    except requests.exceptions.Timeout:
        return jsonify({'message': 'Request to price service timed out'}), 504
    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling price service: {e}")
        return jsonify({'message': 'Failed to call price service', 'error': str(e)}), 500

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"message": "Hello, bookStore!"}), 200

def get_version() -> str:
    """读取版本号文件version.txt，如果不存在则返回 unknown"""
    try:
        with open("version.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "unknown"


if __name__ == '__main__':
    version = get_version()
    logging.info(f"Starting Book Store version: {version}")
    # 启动Flask应用，监听0.0.0.0:5000端口
    app.run(debug=True, host='0.0.0.0', port=5000)
