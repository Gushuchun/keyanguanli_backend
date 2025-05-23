from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from apps.user.models import SMSCode, UserModel
from apps.student.models import Student
from apps.teacher.models import Teacher
from django.contrib.auth.hashers import make_password
from django.utils import timezone
import logging

logger = logging.getLogger('user')

class ResetPasswordView(APIView):
    def post(self, request):
        username = request.username
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not all([username, old_password, new_password]):
            return Response({
                "message": "用户名、旧密码和新密码都是必填项",
                "code": 400
            }, status=status.HTTP_200_OK)

        user = authenticate(username=username, password=old_password)

        if user is None:
            return Response({
                "message": "旧密码错误",
                "code": 400
            }, status=status.HTTP_200_OK)

        try:
            # 修改密码
            user.password = make_password(new_password)
            user.save(update_fields=['password'])
            logger.info(f"用户 {username} 成功修改了密码")
            return Response({
                "message": "密码修改成功",
                "code": 200
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"修改密码失败: {e}")
            return Response({
                "message": "修改密码失败",
                "code": 500
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        new_password = request.data.get('new_password')

        if not all([email, code, new_password]):
            return Response({
                "message": "邮箱、验证码和新密码都是必填项",
                "code": 400
            }, status=status.HTTP_200_OK)

        try:
            # 查找验证码是否匹配
            sms_code = SMSCode.objects.filter(email=email, code=code).first()
            if not sms_code:
                return Response({
                    "message": "验证码错误",
                    "code": 400
                }, status=status.HTTP_200_OK)

            if (timezone.now() - sms_code.update_time).total_seconds() > settings.SMS_CODE_EXPIRE:
                return Response({"message": "验证码已过期", "code": 400}, status=status.HTTP_200_OK)

            # 找到对应的用户

            user = UserModel.objects.filter(email=email).first()

            if user is None:
                return Response({
                    "message": "未找到与该邮箱关联的用户",
                    "code": 400
                }, status=status.HTTP_200_OK)

            # 修改密码
            user.set_password(new_password)
            user.save()

            # 删除已使用的验证码
            sms_code.delete()

            logger.info(f"用户 {email} 通过验证码重置了密码")
            return Response({
                "message": "密码重置成功",
                "code": 200
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"密码重置失败: {e}")
            return Response({
                "message": "密码重置失败",
                "code": 500
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
