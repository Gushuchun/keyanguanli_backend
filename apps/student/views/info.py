from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.response import Response
from apps.student.models import Student
from apps.student.serializers import StudentSerializer, StudentAvatarSerializer, StudentNotMeSerializer
import logging

from apps.user.models import UserModel

logger = logging.getLogger('student')

class StudentInfoViewSet(ViewSet):
    def list(self, request):
        """获取用户信息"""
        try:
            user = Student.objects.get(username=request.username, state=1)
            serializer = StudentSerializer(user)

            logger.info(f"用户 {user.username} 查询个人信息成功")
            return Response(serializer.data)

        except Student.DoesNotExist:
            logger.info(f"用户 {request.username} 不存在")
            return Response(
                {'error': '用户不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

    def update(self, request, pk=None):
        """更新用户信息"""
        try:
            current_user = Student.objects.get(username=request.username, state=1)

            # 权限验证
            if str(current_user.id) != pk:
                logger.info(f"用户 {current_user.username} 尝试修改他人信息 (ID: {pk})")
                return Response(
                    {'error': '无权修改他人信息'},
                    status=status.HTTP_403_FORBIDDEN
                )

            user = Student.objects.get(id=pk)

            email  = request.data.get('email')
            if email and UserModel.objects.filter(email=email).exists():
                return Response(
                    {'message': '邮箱已被注册', 'code': 400},
                    status=status.HTTP_200_OK
                )

            # 使用Serializer处理
            serializer = StudentSerializer(
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
                    status=status.HTTP_200_OK
                )

            serializer.save()

            logger.info(f"用户 {current_user.username} 更新信息成功")
            return Response({
                'message': '信息更新成功',
                'data': StudentSerializer(user).data  # 返回完整序列化数据
            })

        except Student.DoesNotExist:
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
            current_user = Student.objects.get(sn=request.sn, state=1)

            # 使用头像序列化器处理头像上传
            serializer = StudentAvatarSerializer(current_user, data={'avatar': request.FILES.get('avatar')}, partial=True)

            if not serializer.is_valid():
                logger.info(f"用户 {current_user.username} 上传头像失败: {serializer.errors}")
                return Response(
                    {'message': '头像上传失败', 'data': serializer.errors, 'code': 400}
                )

            serializer.save()

            logger.info(f"用户 {current_user.username} 上传头像成功")
            return Response({
                'message': '头像上传成功',
                'data': StudentSerializer(current_user).data
            })

        except Student.DoesNotExist:
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
            current_user = Student.objects.get(sn=request.sn, state=1)
            avatar_url = current_user.avatar
            return Response({'avatar_url': avatar_url})
        except Student.DoesNotExist:
            logger.warning(f"用户 {request.sn} 不存在")
            return Response(
                {'message': '用户不存在', 'code': 404}
            )


    @action(detail=False, methods=['post'], url_path='get-student-info')
    def get_student_info(self, request):
        """获取学生信息"""
        sn = request.data.get('sn')
        try:
            student = Student.objects.get(sn=sn, state=1)
            serializer = StudentNotMeSerializer(student)
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response({'message': '学生不存在'}, status=status.HTTP_404_NOT_FOUND)