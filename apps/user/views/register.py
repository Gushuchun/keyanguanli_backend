from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from apps.user.serializers import StudentRegistrationSerializer, TeacherRegistrationSerializer

User = get_user_model()


class Register(viewsets.ViewSet):
    """
    用户注册
    """
    permission_classes = [permissions.AllowAny]  # 允许未认证用户访问

    def create(self, request):
        """
        用户注册接口
        请求示例：
        {
            "role": "student|teacher",
            "username": "用户名",
            "password": "密码",
            "college_id": 1,
            "phone": "13800138000",
            // 学生特有字段
            "cn": "身份证号",
            "team_id": "团队ID",
            // 教师特有字段
            "email": "邮箱",
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_serializer(self, *args, **kwargs):
        role = self.request.data.get('role', 'student')
        if role == 'teacher':
            return TeacherRegistrationSerializer(*args, **kwargs)
        return StudentRegistrationSerializer(*args, **kwargs)