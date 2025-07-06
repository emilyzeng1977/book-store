from flask import request, jsonify, make_response
from flasgger import swag_from

from . import app
from .auth import get_secret_hash
from .config import *
from .swagger_defs import auth_login_doc

cognito_client = app.cognito_client

@app.route('/auth/login', methods=['POST'])
@swag_from(auth_login_doc)
def login():
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'username and password required'}), 400

    try:
        resp = cognito_client.admin_initiate_auth(
            UserPoolId=COGNITO_USER_POOL_ID,
            ClientId=COGNITO_CLIENT_ID,
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters={
                'USERNAME': data['username'],
                'PASSWORD': data['password'],
                'SECRET_HASH': get_secret_hash(data['username'])
            }
        )
        access_token = resp['AuthenticationResult']['AccessToken']
        response = make_response(jsonify(resp['AuthenticationResult']))
        response.set_cookie('Authorization', f'Bearer {access_token}',
                            httponly=COOKIE_HTTPONLY,
                            secure=COOKIE_SECURE,
                            samesite=COOKIE_SAMESITE,
                            domain=COOKIE_DOMAIN,
                            max_age=COOKIE_MAX_AGE)
        return response
    except Exception as e:
        return jsonify({'error': 'Authentication failed', 'details': str(e)}), 401
