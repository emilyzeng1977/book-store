import os

def get_env_variable(key: str, default_value: str) -> str:
    """获取环境变量，若未设置则使用默认值"""
    return os.getenv(key, default_value)

# MongoDB Atlas
ATLAS_MONGO_USER = get_env_variable("ATLAS_MONGO_USER", "tom")
ATLAS_MONGO_PASSWORD = get_env_variable("ATLAS_MONGO_PASSWORD", "abc123456")
ATLAS_MONGO_HOST = get_env_variable("ATLAS_MONGO_HOST", "emily-demo.unlcmad.mongodb.net")
ATLAS_MONGO_APP_NAME = get_env_variable("ATLAS_MONGO_APP_NAME", "emily-demo")
ATLAS_MONGO_DB = get_env_variable("ATLAS_MONGO_DB", "book-store")

# AWS Cognito
AWS_REGION = get_env_variable('AWS_REGION', 'ap-southeast-2')
COGNITO_USER_POOL_ID = get_env_variable('COGNITO_USER_POOL_ID', 'ap-southeast-2_09CeFqveZ')
COGNITO_CLIENT_ID = get_env_variable('COGNITO_CLIENT_ID', '1ktmj89m2g93t3pbb2u24mbl6s')
COGNITO_CLIENT_SECRET = get_env_variable('COGNITO_CLIENT_SECRET', 'v3anmuq5t83p1b8i32m3r54hcjctjjgtl9de46fgkf54a5iqi2r')

# Cookie 配置
COOKIE_HTTPONLY = get_env_variable('COOKIE_HTTPONLY', 'True') == 'True'
COOKIE_SECURE = get_env_variable('COOKIE_SECURE', 'True') == 'True'
COOKIE_SAMESITE = get_env_variable('COOKIE_SAMESITE', 'None')
COOKIE_DOMAIN = get_env_variable('COOKIE_DOMAIN', '.be-devops.shop')
COOKIE_MAX_AGE = int(get_env_variable('COOKIE_MAX_AGE', '3600'))

# 认证是否启用
AUTH_ENABLE = get_env_variable('AUTH_ENABLE', 'true').lower() == 'true'

# CORS 允许来源
CORS_ORIGINS = get_env_variable('CORS_ORIGINS', 'https://dev.be-devops.shop')

PRICE_SERVER = get_env_variable('PRICE_SERVER', 'host.docker.internal')
PRICE_PORT = get_env_variable('PRICE_PORT', '5000')

# Enable AWS XRAY
AWS_XRAY_ENABLE = get_env_variable('AWS_XRAY_ENABLE', 'false').lower() == 'true'