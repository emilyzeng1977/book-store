auth_login_doc = {
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
}