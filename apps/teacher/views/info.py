from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.response import Response
from apps.teacher.models import Teacher
from apps.teacher.serializers import TeacherInfoSerializer
import logging

logger = logging.getLogger('student')

from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
class TeacherInfoViewSet(ViewSet):
    def list(self, request):
        """获取用户信息"""
        try:
            user = Teacher.objects.get(username=request.username, state=1)
            serializer = TeacherInfoSerializer(user)

            logger.info(f"用户 {user.username} 查询个人信息成功")
            return Response(serializer.data)

        except Teacher.DoesNotExist:
            logger.info(f"用户 {request.username} 不存在")
            return Response(
                {'error': '用户不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

    def update(self, request, pk=None):
        """更新用户信息"""
        try:
            current_user = Teacher.objects.get(username=request.username, state=1)

            # 权限验证
            if str(current_user.id) != pk:
                logger.info(f"用户 {current_user.username} 尝试修改他人信息 (ID: {pk})")
                return Response(
                    {'error': '无权修改他人信息'},
                    status=status.HTTP_403_FORBIDDEN
                )

            user = Teacher.objects.get(id=pk)

            # 使用Serializer处理
            serializer = TeacherInfoSerializer(
                user,
                data=request.data,
                partial=True,
                context={'request': request}
            )

            if not serializer.is_valid():
                logger.info(
                    f"用户 {current_user.username} 数据验证失败: "
                    f"{serializer.errors}"
                )
                return Response(
                    {'error': '数据验证失败', 'details': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer.save()

            logger.info(f"用户 {current_user.username} 更新信息成功")
            return Response({
                'message': '信息更新成功',
                'data': TeacherInfoSerializer(user).data  # 返回完整序列化数据
            })

        except Teacher.DoesNotExist:
            logger.info(f"用户ID {pk} 不存在")
            return Response(
                {'error': '用户不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"更新用户信息错误: {str(e)}")
            return Response(
                {'error': '服务器内部错误'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )