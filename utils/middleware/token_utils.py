import uuid
import jwt
import datetime
from django.conf import settings

JWT_EXPIRATION_DELTA = datetime.timedelta(days=1)

def generate_token(user_id, role="student"):
    SECRET_KEY = settings.SECRET_KEY

    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.datetime.utcnow() + JWT_EXPIRATION_DELTA,
        'iat': datetime.datetime.utcnow(),
        'jti': str(uuid.uuid4())
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS512')
    return token

if __name__ == '__main__':
    token = generate_token(1, 'admin')
    print(token)