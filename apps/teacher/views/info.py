from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.college.models import College
from apps.teacher.models import Teacher
from apps.teacher.serializers import TeacherInfoSerializer, TeacherAvatarSerializer
import logging

from apps.user.models import UserModel

logger = logging.getLogger('teacher')

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

            email  = request.data.get('email')
            if email and UserModel.objects.filter(email=email).exists():
                return Response(
                    {'message': '邮箱已被注册', 'code': 400},
                    status=status.HTTP_200_OK
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

    @action(detail=False, methods=['post'])
    def update_avatar(self, request):
        """更新用户头像"""
        try:
            current_user = Teacher.objects.get(sn=request.sn, state=1)

            # 获取并验证上传的文件
            avatar = request.FILES.get('avatar')
            if not avatar:
                return Response(
                    {'message': '没有上传头像', 'code': 400},
                )

            # 使用头像序列化器处理头像上传
            serializer = TeacherAvatarSerializer(current_user, data={'avatar': avatar}, partial=True)

            if not serializer.is_valid():
                logger.info(f"用户 {current_user.username} 上传头像失败: {serializer.errors}")
                return Response(
                    {'message': '头像上传失败', 'data': serializer.errors, 'code': 400}
                )

            serializer.save()

            logger.info(f"用户 {current_user.username} 上传头像成功")
            return Response({
                'message': '头像上传成功',
                'data': TeacherInfoSerializer(current_user).data
            })

        except Teacher.DoesNotExist:
            logger.warning(f"用户 {request.sn} 不存在")
            return Response(
                {'message': '用户不存在', 'code': 404}
            )
        except Exception as e:
            logger.error(f"更新头像失败: {str(e)}")
            return Response(
                {'message': '服务器内部错误', 'code': 500},
            )

    @action(detail=False, methods=['get'])
    def get_avatar(self, request):
        """获取用户头像"""
        try:
            current_user = Teacher.objects.get(sn=request.sn, state=1)
            avatar_url = current_user.avatar
            return Response({'avatar_url': avatar_url})
        except Teacher.DoesNotExist:
            logger.warning(f"用户 {request.sn} 不存在")
            return Response(
                {'message': '用户不存在', 'code': 404}
            )

    @action(detail=False, methods=['post'], url_path='get-teacher-info')
    def get_teacher_info(self, request):
        """获取学生信息"""
        sn = request.data.get('sn')
        try:
            teacher = Teacher.objects.get(sn=sn, state=1)
            college = College.objects.filter(id=teacher.college_id).first()
            return Response({
                'college': college.name,
                'avatar': teacher.avatar if teacher.avatar else None,
                'username': teacher.username,
                'id': teacher.id,
                'note': teacher.note
            })
        except Teacher.DoesNotExist:
            return Response({'message': '教师不存在'}, status=status.HTTP_404_NOT_FOUND)