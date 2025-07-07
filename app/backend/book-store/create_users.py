import datetime

from app import app
from app import config  # 导入 config 模块
from botocore.exceptions import ClientError

# Cognito 和 MongoDB 客户端
cognito = app.cognito_client
users = app.db.users

# 示例用户列表
user_list = [
    {"username": "admin@gmail.com", "password": "*Abc12345", "role": "admin"},
    {"username": "tom@gmail.com", "password": "*Abc12345", "role": "user"},
    {"username": "emily@gmail.com", "password": "*Abc12345", "role": "user"},
]

COGNITO_USER_POOL_ID = config.COGNITO_USER_POOL_ID

for u in user_list:
    username = u["username"]

    try:
        # Step 1: 先检查 Cognito 中是否已存在用户
        try:
            cognito.admin_get_user(UserPoolId=COGNITO_USER_POOL_ID, Username=username)
            print(f"⚠️ Cognito user {username} already exists, skipping creation.")
            continue
        except cognito.exceptions.UserNotFoundException:
            pass  # 用户不存在，可以继续创建

        # Step 2: 创建 Cognito 用户
        cognito.admin_create_user(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username=username,
            TemporaryPassword=u["password"],
            MessageAction='SUPPRESS',
            UserAttributes=[
                {"Name": "email", "Value": username},
                {"Name": "email_verified", "Value": "true"}
            ]
        )

        # Step 3: 设置密码为永久
        cognito.admin_set_user_password(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username=username,
            Password=u["password"],
            Permanent=True
        )

        # Step 4: 获取 sub
        user_detail = cognito.admin_get_user(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username=username
        )
        sub = next(attr["Value"] for attr in user_detail["UserAttributes"] if attr["Name"] == "sub")

        # Step 5: 检查 MongoDB 中是否已存在该用户
        if users.find_one({"cognito_sub": sub}) or users.find_one({"username": username}):
            print(f"⚠️ MongoDB already contains user {username}, skipping DB insertion.")
        else:
            # Step 6: 写入 MongoDB
            users.insert_one({
                "cognito_sub": sub,
                "username": username,
                "role": u["role"],
                "created_at": datetime.datetime.utcnow()
            })
            print(f"✅ Created {username} with role {u['role']}")

    except ClientError as e:
        print(f"❌ AWS error creating {username}: {e}")
    except Exception as e:
        print(f"❌ Failed to create {username}: {e}")
