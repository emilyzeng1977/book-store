import logging
import os
import socket

import requests
from bson.objectid import ObjectId
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from pymongo import MongoClient, errors

import hmac
import hashlib
import base64
import boto3
from botocore.exceptions import ClientError

from jose import jwk, jwt
from jose.exceptions import JWTError, ExpiredSignatureError, JWTClaimsError

from functools import wraps

from flasgger import Swagger, swag_from

# Flask 应用初始化
app = Flask(__name__)

swagger = Swagger(app)

# 日志配置，INFO级别，方便查看运行信息
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

def get_env_variable(key: str, default_value: str) -> str:
    """获取环境变量，若未设置则使用默认值"""
    value = os.getenv(key)
    return value if value else default_value

# ----------------------
# MongoDB Atlas 配置参数（可通过环境变量覆盖）
# ----------------------
atlas_mongo_user = get_env_variable("ATLAS_MONGO_USER", "tom")
atlas_mongo_password = get_env_variable("ATLAS_MONGO_PASSWORD", "abc123456")
atlas_mongo_host = get_env_variable("ATLAS_MONGO_HOST", "emily-demo.unlcmad.mongodb.net")
atlas_mongo_app_name = get_env_variable("ATLAS_MONGO_APP_NAME", "emily-demo")
atlas_mongo_db = get_env_variable("ATLAS_MONGO_DB", "book-store")

# 需要在环境变量里配置，或者硬编码也行（不推荐）
aws_region = get_env_variable('AWS_REGION', 'ap-southeast-2')
cognito_user_pool_id = get_env_variable('COGNITO_USER_POOL_ID', 'ap-southeast-2_09CeFqveZ')
cognito_client_id = get_env_variable('COGNITO_CLIENT_ID', '1ktmj89m2g93t3pbb2u24mbl6s')
cognito_client_secret = get_env_variable('COGNITO_CLIENT_SECRET', 'v3anmuq5t83p1b8i32m3r54hcjctjjgtl9de46fgkf54a5iqi2r')

cors_origins_str = get_env_variable('CORS_ORIGINS', 'http://localhost:3000')
cookie_domain = get_env_variable('COOKIE_DOMAIN', 'localhost')

auth_enable = get_env_variable('AUTH_ENABLE', 'false').lower() == 'true'

cors_origins = [origin.strip() for origin in cors_origins_str.split(',') if origin.strip()]
CORS(app,
     supports_credentials=True,
     origins=cors_origins) # # 需要完整指定端口

cognito_issuer = f'https://cognito-idp.{aws_region}.amazonaws.com/{cognito_user_pool_id}'
jwks_url  = f'{cognito_issuer}/.well-known/jwks.json'

# 下载并缓存 JWKs
jwks = requests.get(jwks_url).json()['keys']

cognito_client = boto3.client('cognito-idp', region_name=aws_region)

# 生成 MongoDB 连接字符串
atlas_mongo_uri = (
    f"mongodb+srv://{atlas_mongo_user}:{atlas_mongo_password}@{atlas_mongo_host}"
    f"/?retryWrites=true&w=majority&appName={atlas_mongo_app_name}"
)

# 初始化 MongoDB 连接
try:
    client = MongoClient(atlas_mongo_uri, serverSelectionTimeoutMS=3000)  # 3秒连接超时
    db = client[atlas_mongo_db]
    collection = db.books
    logging.info(f"Connected to MongoDB database: {atlas_mongo_db}")
except Exception as e:
    logging.error(f"Error connecting to MongoDB: {e}")
    raise

def get_secret_hash(username):
    message = username + cognito_client_id
    dig = hmac.new(cognito_client_secret.encode('utf-8'),
                   message.encode('utf-8'),
                   hashlib.sha256).digest()
    return base64.b64encode(dig).decode()

def get_public_key(token):
    try:
        headers = jwt.get_unverified_header(token)
    except JWTError as e:
        raise Exception(f"Invalid token header: {e}")

    kid = headers.get('kid')
    if not kid:
        raise Exception("Token header missing 'kid'")

    key_data = next((k for k in jwks if k.get('kid') == kid), None)
    if not key_data:
        raise Exception("Public key not found in JWKs")

    try:
        # return jwk.construct(key_data)
        key_obj = jwk.construct(key_data)
        return key_obj.to_pem().decode('utf-8')  # ✅ 返回 PEM 格式的 key
    except Exception as e:
        raise Exception(f"Failed to construct public key from JWK: {e}")

def verify_token(token):
    try:
        public_key = get_public_key(token)
        decoded = jwt.decode(
            token,
            key=public_key,
            algorithms=["RS256"],
            issuer=cognito_issuer
        )
        return decoded
    except ExpiredSignatureError:
        raise Exception("Token has expired")
    except JWTClaimsError as e:
        raise Exception(f"Invalid claims: {e}")
    except JWTError as e:
        raise Exception(f"JWT decode error: {e}")
    except Exception as e:
        raise Exception(f"Token verification failed: {e}")


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not auth_enable:
            # 如果关闭认证开关，直接执行目标函数
            return f(*args, **kwargs)
        token = None

        # 先检查 Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        # 如果 header 没有 token，再检查 Cookie 里的 Authorization
        if not token:
            cookie_auth = request.cookies.get('Authorization')
            if cookie_auth and cookie_auth.startswith('Bearer '):
                token = cookie_auth.split(' ')[1]
            else:
                # 如果 cookie 里的 Authorization 不是 Bearer 开头，直接用整个值作为 token
                token = cookie_auth

        if not token:
            return jsonify({'error': 'Missing token'}), 401

        try:
            verify_token(token)
        except Exception as e:
            return jsonify({'error': 'Invalid token', 'details': str(e)}), 401

        return f(*args, **kwargs)

    return decorated

# ----------------------
# 路由定义
# ----------------------

@app.route('/login', methods=['POST'])
@swag_from({
    'tags': ['Auth'],
    'summary': '用户登录',
    'description': '使用 Cognito 进行用户认证，成功后返回认证结果（包含 AccessToken）',
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['username', 'password'],
                'properties': {
                    'username': {'type': 'string', 'example': 'testuser'},
                    'password': {'type': 'string', 'example': 'TestPassword123'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': '登录成功，返回认证信息',
            'schema': {
                'type': 'object',
                'properties': {
                    'AccessToken': {'type': 'string'},
                    'IdToken': {'type': 'string'},
                    'RefreshToken': {'type': 'string'},
                    'ExpiresIn': {'type': 'integer'}
                }
            }
        },
        400: {
            'description': '缺少用户名或密码',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'username and password required'}
                }
            }
        },
        401: {
            'description': '认证失败',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'NotAuthorizedException'},
                    'message': {'type': 'string', 'example': 'Incorrect username or password.'}
                }
            }
        }
    }
})
def login():
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'username and password required'}), 400

    username = data['username']
    password = data['password']

    try:
        resp = cognito_client.admin_initiate_auth(
            UserPoolId=cognito_user_pool_id,
            ClientId=cognito_client_id,
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
        # response.set_cookie(
        #     'Authorization',
        #     f'Bearer {access_token}',
        #     httponly=True,  # JS 不能读取，防止XSS
        #     secure=False,  # 本地测试用 False, 生产环境请改成 True (只会在 HTTPS 请求中被浏览器接收或发送) ,当samesite为None时必须为True
        #     samesite='Lax',  # Lax|CSRF防护，可根据需求改为 'Strict', 注意，为None时候必须要HTTPS
        #     # domain=cookie_domain,
        #     max_age=3600  # token有效期，比如1小时
        # )
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
@swag_from({
    'tags': ['Books'],
    'summary': '获取所有书籍',
    'responses': {
        200: {
            'description': '返回所有书籍列表',
            'schema': {
                'type': 'object',
                'properties': {
                    'books': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                '_id': {
                                    'type': 'string',
                                    'example': '60f7b0b6e13a4b3e2f4a6789'
                                },
                                'title': {
                                    'type': 'string',
                                    'example': 'Book Title'
                                },
                                'author': {
                                    'type': 'string',
                                    'example': 'Author Name'
                                }
                            }
                        }
                    }
                }
            }
        },
        504: {
            'description': '查询超时',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Query timed out'
                    }
                }
            }
        },
        500: {
            'description': '数据库错误',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'MongoDB query error'
                    }
                }
            }
        }
    }
})
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
@swag_from({
    'tags': ['Books'],
    'summary': '获取指定书籍详情',
    'parameters': [
        {
            'name': 'book_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': '书籍的 MongoDB ID'
        }
    ],
    'responses': {
        200: {
            'description': '成功返回书籍详情',
            'schema': {
                'type': 'object',
                'properties': {
                    '_id': {'type': 'string', 'example': '60f7b0b6e13a4b3e2f4a6789'},
                    'title': {'type': 'string', 'example': 'Book Title'},
                    'author': {'type': 'string', 'example': 'Author Name'}
                }
            }
        },
        400: {
            'description': '无效的书籍 ID',
            'schema': {'type': 'object', 'properties': {'error': {'type': 'string'}}}
        },
        404: {
            'description': '未找到书籍',
            'schema': {'type': 'object', 'properties': {'error': {'type': 'string'}}}
        }
    }
})
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
@swag_from({
    'tags': ['Books'],
    'summary': '添加新书籍',
    'description': '添加一本新书，要求提供 title 和 author 字段。',
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['title', 'author'],
                'properties': {
                    'title': {'type': 'string', 'example': 'Book Title'},
                    'author': {'type': 'string', 'example': 'Author Name'}
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': '创建成功',
            'schema': {
                'type': 'object',
                'properties': {
                    '_id': {'type': 'string', 'example': '60f7b0b6e13a4b3e2f4a6789'},
                    'title': {'type': 'string', 'example': 'Book Title'},
                    'author': {'type': 'string', 'example': 'Author Name'}
                }
            }
        },
        400: {
            'description': '缺少 title 或 author 字段',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'The new book must have a title and author'}
                }
            }
        },
        500: {
            'description': '数据库插入失败',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Failed to add book'}
                }
            }
        }
    }
})
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
@swag_from({
    'tags': ['Books'],
    'summary': '根据书籍ID删除书籍',
    'parameters': [
        {
            'name': 'book_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': '书籍的 MongoDB ID'
        }
    ],
    'responses': {
        200: {
            'description': '书籍删除成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Book deleted'}
                }
            }
        },
        400: {
            'description': '无效的书籍 ID',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Invalid book ID'}
                }
            }
        },
        404: {
            'description': '未找到书籍',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Book not found'}
                }
            }
        },
        500: {
            'description': '删除书籍失败',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Failed to delete book'}
                }
            }
        }
    }
})
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
    price_server = get_env_variable('PRICE_SERVER', 'host.docker.internal')
    price_port = get_env_variable('PRICE_PORT', '5000')

    server_name = socket.gethostname()
    try:
        server_ip = socket.gethostbyname(server_name)
    except socket.gaierror:
        server_ip = "127.0.0.1"

    book_id = request.args.get('book_id')
    price_service_url = f"http://{price_server}:{price_port}/price"
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

# @app.route('/healthz', methods=['GET'])
# def health_check():
#     """健康检查接口，返回服务状态"""
#     return jsonify({"status": "ok"}), 200

@app.route('/', methods=['GET'])
@swag_from({
    'tags': ['Health Check'],
    'summary': '服务健康检查',
    'description': '用于验证服务是否正常运行',
    'responses': {
        200: {
            'description': '服务运行正常',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'example': 'Hello, bookStore!'
                    }
                }
            }
        }
    }
})
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
