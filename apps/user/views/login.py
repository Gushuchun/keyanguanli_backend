from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from apps.user.models import UserModel
from utils.token_utils import generate_token

class LoginView(APIView):
    def post(self, request):
        # 获取请求中的用户名和密码
        username = request.data.get('username')
        password = request.data.get('password')

        # 验证用户名和密码
        user = authenticate(username=username, password=password)

        if user is not None:
            # 生成 JWT token
            token = generate_token(user.id, user.role)
            return Response({
                'token': token,
                'user_id': user.id,
                'username': user.username,
                'role': user.role
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': '用户名或密码错误'}, status=status.HTTP_401_UNAUTHORIZED)