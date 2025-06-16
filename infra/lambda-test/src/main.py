import boto3

from jose import jwk, jwt
from jose.exceptions import JWTError, ExpiredSignatureError, JWTClaimsError

import os
import requests

USER_POOL_ID = os.environ["USER_POOL_ID"]
AWS_REGION = 'ap-southeast-2'
APP_CLIENT_ID = os.environ["APP_CLIENT_ID"]

cognito_issuer = f'https://cognito-idp.{AWS_REGION}.amazonaws.com/{USER_POOL_ID}'
jwks_url  = f'{cognito_issuer}/.well-known/jwks.json'

# 下载并缓存 JWKs
jwks = requests.get(jwks_url).json()['keys']

cognito_client = boto3.client('cognito-idp', region_name=AWS_REGION)

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


def lambda_handler(event, context):
    try:
        token = event["headers"].get("authorization") or event["headers"].get("Authorization", "")
        token = token.replace("Bearer ", "")

        public_key = get_public_key(token)
        decoded = jwt.decode(
            token,
            key=public_key,
            algorithms=["RS256"],
            issuer=cognito_issuer
        )

        return {
            "isAuthorized": True,
            "context": {
                "username": decoded.get("username")
            }
        }

    except Exception as e:
        print("Auth error:", str(e))
        return {
            "isAuthorized": False
        }
