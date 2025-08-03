import os

def get_env_variable(key: str, default_value: str) -> str:
    """获取环境变量，若未设置则使用默认值"""
    return os.getenv(key, default_value)

# Enable AWS XRAY
AWS_XRAY_ENABLE = get_env_variable('AWS_XRAY_ENABLE', 'false').lower() == 'true'