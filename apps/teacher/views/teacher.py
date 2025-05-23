from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.response import Response
from apps.teacher.models import Teacher
from apps.teacher.serializers import TeacherListSerializer
import logging

logger = logging.getLogger('student')


class TeacherList(ViewSet):
    def list(self, request):
        """获取用户列表"""
        try:
            queryset = Teacher.objects.filter(state=1)
            serializer = TeacherListSerializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"获取用户列表失败: {str(e)}", exc_info=True)
            return Response(
                {'error': '服务器内部错误'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


