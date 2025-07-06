import logging

import requests
from flask import jsonify, request

import hmac
import hashlib
import base64

from jose import jwk, jwt
from jose.exceptions import JWTError, ExpiredSignatureError, JWTClaimsError

from functools import wraps

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


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # 关闭认证或是预检请求，直接放行
        func_name = f.__name__

        if not AUTH_ENABLE:
            logging.debug(f"[token_required] Skipped (auth disabled) - Function: {func_name}")
            return f(*args, **kwargs)

        if request.method == 'OPTIONS':
            logging.debug(f"[token_required] Skipped (OPTIONS request) - Function: {func_name}")
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