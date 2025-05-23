import jwt
from django.http import JsonResponse
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
import logging
from apps.student.models import Student
from apps.teacher.models import Teacher

logger = logging.getLogger('user')

class TokenAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 忽略登录和注册接口的请求
        if request.path in ['/api/user/login/',
                            '/api/user/register/',
                            '/api/college/public/',
                            '/api/user/sms_send/',
                            '/api/user/code_login/',
                            '/api/user/forgot-password/',]:
            return None

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            logger.info('未提供认证信息')
            return JsonResponse({'error': '未提供认证信息'}, status=400)

        # 检查并提取JWT token
        try:
            # 分割"Bearer "或"JWT "前缀
            parts = auth_header.split()
            if len(parts) != 2:
                raise ValueError("请求头头格式错误")

            scheme, token = parts
            if scheme.lower() not in ('bearer', 'jwt'):
                raise ValueError("认证方案不支持")

        except ValueError as e:
            logger.info('请求头头格式错误')
            return JsonResponse({'error': str(e)}, status=400)

        try:
            # 解码 token 时，验证过期时间和签名
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS512'])
            user_id = payload['user_id']

            User = get_user_model()
            request.user = User.objects.get(id=user_id, is_active=True)
            request.username = request.user.username
            if payload['role'] == 'student':
                request.id = Student.objects.get(username=request.user.username).id
                request.sn = Student.objects.get(username=request.user.username).sn
            elif payload['role'] =='teacher':
                request.id = Teacher.objects.get(username=request.user.username).id
                request.sn = Teacher.objects.get(username=request.user.username).sn
            request.role = payload['role']

        except jwt.ExpiredSignatureError:
            logger.info('token已过期')
            return JsonResponse({'message': 'token已过期', 'code': 400}, status=200)
        except jwt.InvalidTokenError:
            logger.info('无效的token')
            return JsonResponse({'message': '无效的token', 'code': 400}, status=200)
        except User.DoesNotExist:
            logger.info('用户不存在')
            return JsonResponse({'message': '用户不存在', 'code': 400}, status=200)

        return None