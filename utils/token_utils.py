import jwt
import datetime
from django.conf import settings

SECRET_KEY = settings.SECRET_KEY  # 用你的密钥
JWT_EXPIRATION_DELTA = datetime.timedelta(days=1)  # 1天有效期


# 生成带有角色等自定义信息的 token
def generate_token(user_id, role="student"):
    """
    生成带有角色信息的 JWT token
    :param user_id: 用户 ID
    :param role: 用户角色 (例如 'admin', 'user')
    :return: token
    """
    payload = {
        'user_id': user_id,  # 用户ID
        'role': role,  # 用户角色
        'exp': datetime.datetime.utcnow() + JWT_EXPIRATION_DELTA,  # 过期时间
        'iat': datetime.datetime.utcnow()  # 签发时间
    }

    # 使用密钥进行编码
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

if __name__ == '__main__':
    token = generate_token(1, 'admin')
    print(token)