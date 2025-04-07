import jwt
from django.http import JsonResponse
from django.conf import settings
from rest_framework import status
from django.utils.deprecation import MiddlewareMixin

from django.contrib.auth import get_user_model


class TokenAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 忽略登录和注册接口的请求
        if request.path in ['/api/user/login/', '/api/user/register/']:
            return None

        token = request.headers.get('Authorization')
        if not token:
            return JsonResponse({'error': '未提供token'}, status=401)

        try:
            # 解码 token 时，验证过期时间和签名
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS512'])
            user_id = payload['user_id']

            User = get_user_model()
            request.user = User.objects.get(id=user_id, is_active=True)
            request.username = request.user.username
            request.role = payload['role']

        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'token已过期'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': '无效的token'}, status=401)
        except User.DoesNotExist:
            return JsonResponse({'error': '用户不存在'}, status=401)

        return None