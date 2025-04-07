import uuid

import jwt
import datetime
from django.conf import settings

JWT_EXPIRATION_DELTA = datetime.timedelta(days=1)  # 1天有效期


# 生成带有角色等自定义信息的 token
def generate_token(user_id, role="student"):
    """
    生成带有角色信息的 JWT token
    :param user_id: 用户 ID
    :param role: 用户角色 (例如 'admin', 'user')
    :return: token
    """
    SECRET_KEY = settings.SECRET_KEY

    payload = {
        'user_id': user_id,  # 用户ID
        'role': role,  # 用户角色
        'exp': datetime.datetime.utcnow() + JWT_EXPIRATION_DELTA,
        'iat': datetime.datetime.utcnow(),  # 签发时间
        'jti': str(uuid.uuid4())  # 使用UUID生成唯一的JWT ID，防止重放攻击
    }

    # 使用强加密算法
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS512')
    return token

if __name__ == '__main__':
    token = generate_token(1, 'admin')
    print(token)