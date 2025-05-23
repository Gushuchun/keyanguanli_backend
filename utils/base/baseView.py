from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.http import Http404
from utils.base.response_formatter import format_validation_error, format_permission_denied, format_http404_error
import logging
logger = logging.getLogger('error')


class BaseModelViewSet(viewsets.ModelViewSet):
    """
    继承 ModelViewSet，统一处理常见异常和分页逻辑
    """

    def handle_exception(self, exc):
        if isinstance(exc, ValidationError):
            return format_validation_error(exc)
        elif isinstance(exc, PermissionDenied):
            return format_permission_denied(exc)
        elif isinstance(exc, Http404):
            return format_http404_error(exc)
        else:
            logger.error(f"Unexpected error: {str(exc)}")
            return Response({
                "message": "内部服务器错误",
                "error": str(exc)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def paginate_and_serialize_queryset(self, queryset, custom_serializer=None):
        """
        对查询集进行分页处理并序列化

        参数:
            queryset: 要分页的查询集
            custom_serializer: 可选，自定义序列化器类实例

        返回:
            Response: 包含序列化和分页数据的响应
        """
        # 分页处理
        page = self.paginate_queryset(queryset)

        # 使用自定义序列化器或默认序列化器
        serializer = custom_serializer if custom_serializer else self.get_serializer

        if page is not None:
            serialized_data = serializer(page, many=True).data
            return self.get_paginated_response(serialized_data)

        # 如果没有分页，序列化所有数据
        serialized_data = serializer(queryset, many=True).data
        return Response({"message": "获取成功", "code": 200, "data": serialized_data})

    def success_response(self, data=None, message="操作成功", code=status.HTTP_200_OK):
        """统一成功响应格式"""
        return Response({
            "message": message,
            "data": data,
            "code": code
        })

    def error_response(self, message, code=status.HTTP_400_BAD_REQUEST, error=None):
        """统一错误响应格式"""
        return Response({
            "message": message,
            "error": str(error) if error else None,
            "code": code
        })

