import logging

import requests
from flask import jsonify, request, g

import hmac
import hashlib
import base64

from jose import jwk, jwt
from jose.exceptions import JWTError, ExpiredSignatureError, JWTClaimsError

from functools import wraps

from . import app  # 从 app 中获取 db

from .config import (
    AWS_REGION,
    COGNITO_USER_POOL_ID,
    COGNITO_CLIENT_ID,
    COGNITO_CLIENT_SECRET,
    AUTH_ENABLE
)

cognito_issuer = f'https://cognito-idp.{AWS_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}'
jwks_url  = f'{cognito_issuer}/.well-known/jwks.json'

# 下载并缓存 JWKs

if AUTH_ENABLE:
    jwks = requests.get(jwks_url).json()['keys']

def get_secret_hash(username):
    message = username + COGNITO_CLIENT_ID
    dig = hmac.new(COGNITO_CLIENT_SECRET.encode('utf-8'),
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

def token_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            logging.info("token_required: start token validation")
            token = None
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                logging.info("token_required: token found in Authorization header")
            else:
                logging.info("token_required: no token in Authorization header")

            # Header 里没token时，尝试从 Cookie 拿
            if not token:
                cookie_auth = request.cookies.get('Authorization')
                if cookie_auth and cookie_auth.startswith('Bearer '):
                    token = cookie_auth.split(' ')[1]
                    logging.info("token_required: token found in Cookie with Bearer prefix")
                else:
                    # 可能 Cookie 就是纯 token，不带 Bearer
                    token = cookie_auth
                    if token:
                        logging.info("token_required: token found in Cookie without Bearer prefix")
                    else:
                        logging.info("token_required: no token found in Cookie")


            if not token:
                return jsonify({'error': 'Missing token'}), 401

            try:
                decoded = verify_token(token)
                cognito_sub = decoded.get("sub")
                logging.info(f"token_required: token verified, sub={cognito_sub}")

                user = app.db.users.find_one({"cognito_sub": cognito_sub})
                if not user:
                    return jsonify({'error': 'User not found'}), 403

                g.user = user  # 缓存用户信息

                user_role = user.get('role')

                if role:
                    allowed_roles = [role] if isinstance(role, str) else role
                    if user_role not in allowed_roles:
                        return jsonify({'error': 'Insufficient permissions'}), 403

                return f(*args, **kwargs)

            except Exception as e:
                return jsonify({'error': 'Invalid token', 'details': str(e)}), 401

        return decorated
    return decorator