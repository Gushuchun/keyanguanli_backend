from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.response import Response
from apps.student.models import Student
from apps.student.serializers import StudentListSerializer
import logging

logger = logging.getLogger('student')


class StudentList(ViewSet):
    def list(self, request):
        """获取用户列表"""
        try:
            queryset = Student.objects.filter(state=1)
            serializer = StudentListSerializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"获取用户列表失败: {str(e)}", exc_info=True)
            return Response(
                {'error': '服务器内部错误'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
