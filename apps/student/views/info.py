from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.student.models import Student
from apps.student.serializers import UserSerializer
import logging

logger = logging.getLogger('student')

class UserInfoViewSet(viewsets.ViewSet):

    def list(self, request):
        # 获取当前登录用户的ID
        user = Student.objects.get(username=request.username, state=1)

        # 查询用户信息
        try:
            user_info = Student.objects.get(id=user.id)
            # 返回用户信息

            logger.info(f"用户 {user.username} 查询个人信息成功")
            return Response({
                'user_id': user_info.id,
                'username': user_info.username,
                'email': user_info.email,
                'gender': user_info.gender,
                'phone': user_info.phone,
                'cn': user_info.get_cn(),  # 解密 cn 字段
                'prize_num': user_info.prize_num,
                'race_num': user_info.race_num,
                'team_id': user_info.team_id,
                'is_cap': user_info.is_cap,
                'college_id': user_info.college_id
            })

        except Student.DoesNotExist:
            logger.info(f"用户 {user.username} 查询个人信息失败: 用户不存在")
            return Response({'error': '用户不存在'}, status=404)

    @action(detail=False, methods=['put'])
    def update_info(self, request):
        # 获取当前用户
        user = request.user
        try:
            # 通过 user id 获取用户对象
            user_info = Student.objects.get(id=user.id)

            # 更新用户信息
            user_info.username = request.data.get('username', user_info.username)
            user_info.email = request.data.get('email', user_info.email)
            user_info.tel = request.data.get('phone', user_info.tel)
            user_info.gender = request.data.get('gender', user_info.gender)
            user_info.cn = request.data.get('cn', user_info.cn)

            user_info.save()

            return Response({
                'user_id': user_info.id,
                'username': user_info.username,
                'email': user_info.email,
                'gender': user_info.gender,
                'phone': user_info.tel,
                'cn': user_info.cn
            })

        except Student.DoesNotExist:
            return Response({'error': '用户不存在'}, status=404)
