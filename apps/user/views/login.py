from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.user.tasks import send_email_async
from apps.student.models import Student
from apps.teacher.models import Teacher
from ..models import UserModel, SMSCode
from django.utils import timezone
from utils.middleware.token_utils import generate_token
import logging
from django.contrib.auth import authenticate, login as auth_login, user_login_failed
from django_redis import get_redis_connection
import base64
from utils.keys.rsa_crypt import decryption


logger = logging.getLogger('user')

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = decryption(request.data.get('password'))
        # password = request.data.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)

            # 生成 JWT token
            token = generate_token(user.id, user.role)

            # 获取学生/教师信息
            id, sn = None, None
            if user.role == 'student':
                student = Student.objects.get(username=username)
                id, sn = student.id, student.sn
            elif user.role == 'teacher':
                teacher = Teacher.objects.get(username=username)
                id, sn = teacher.id, teacher.sn

            return Response({
                'code': 200,
                'token': token,
                'user_id': user.id,
                'username': user.username,
                'role': user.role,
                'id': id,
                'sn': sn
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "message": "账号或密码错误",
                "code": 400
            }, status=status.HTTP_200_OK)

class SMS_Send(APIView):
    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({"message": "邮箱不能为空", "code": 400}, status=status.HTTP_400_BAD_REQUEST)

        # 生成6位随机验证码
        import random
        code = ''.join(random.choices('0123456789', k=6))

        # 检查 Redis 中是否有验证码
        redis_conn = get_redis_connection("default")
        cache_key = f'code_{email}'
        existing_code = redis_conn.get(cache_key)

        if existing_code:
            ttl = redis_conn.ttl(cache_key)
            return Response({"message": f"请等待{ttl}秒后再试", "code": 400}, status=status.HTTP_400_BAD_REQUEST)

        # 存储验证码到 Redis，设置过期时间为 SMS_CODE_EXPIRE
        redis_conn.setex(cache_key, settings.SMS_SEND_AGAIN, code)

        # 检查该邮箱是否已有验证码记录
        sms_code, created = SMSCode.objects.get_or_create(email=email)
        sms_code.code = code
        sms_code.save()

        # 发送邮件
        subject = '验证码'
        message = f'您的验证码是：{code}，有效期为5分钟。'
        from_email = '3090228211@qq.com'
        recipient_list = [email]

        # 异步发送邮件
        send_email_async.delay(subject, message, from_email, recipient_list)

        logger.info(f"邮件发送任务已提交: {email}, 验证码: {code}")
        return Response({"message": "验证码已发送", "code": 200}, status=status.HTTP_200_OK)

class CodeLoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        if not email or not code:
            return Response({"message": "邮箱和验证码不能为空", "code": 400}, status=status.HTTP_200_OK)

        try:
            sms_code = SMSCode.objects.get(email=email)
        except SMSCode.DoesNotExist:
            return Response({"message": "验证码错误", "code": 400}, status=status.HTTP_200_OK)

        # 检查过期
        if (timezone.now() - sms_code.update_time).total_seconds() > settings.SMS_CODE_EXPIRE:
            user_login_failed.send(
                sender=self.__class__,
                credentials={'email': email},
                request=request
            )
            return Response({"message": "验证码已过期", "code": 400}, status=status.HTTP_200_OK)

        if sms_code.code != code:
            user_login_failed.send(
                sender=self.__class__,
                credentials={'email': email},
                request=request
            )
            return Response({"message": "验证码错误", "code": 400}, status=status.HTTP_200_OK)

        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            user_login_failed.send(
                sender=self.__class__,
                credentials={'email': email},
                request=request
            )
            return Response({"message": "用户不存在", "code": 404}, status=status.HTTP_200_OK)

        # 标记为验证码登录方式
        request.login_method = 'email'  # 用于信号接收器识别
        auth_login(request, user)  # 触发 user_logged_in 信号

        # 生成 JWT
        token = generate_token(user.id, user.role)

        sms_code.hard_delete()

        # 获取关联信息
        id, sn = None, None
        if user.role == 'student':
            student = Student.objects.get(username=user.username)
            id, sn = student.id, student.sn
        elif user.role == 'teacher':
            teacher = Teacher.objects.get(username=user.username)
            id, sn = teacher.id, teacher.sn

        return Response({
            'code': 200,
            'token': token,
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'id': id,
            'sn': sn
        }, status=status.HTTP_200_OK)