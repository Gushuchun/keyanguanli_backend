from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.http import Http404
import logging

from utils.response_formatter import format_validation_error, format_permission_denied, format_http404_error

logger = logging.getLogger(__name__)

class BaseModelViewSet(viewsets.ModelViewSet):
    """
    继承 ModelViewSet，统一处理常见异常
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
