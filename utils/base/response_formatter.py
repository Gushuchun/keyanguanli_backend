from dbm import error

from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger("error")


def format_validation_error(e):
    """
    格式化 ValidationError 为统一的 JSON 响应结构
    """
    error_detail = e.detail

    # 处理不同类型的错误详情
    if isinstance(error_detail, list):
        # 列表类型的错误（非字段错误）
        first_error_msg = error_detail[0] if error_detail else '参数验证失败'
        error_data = {"non_field_errors": error_detail}
    elif isinstance(error_detail, dict):
        # 字典类型的错误（字段相关错误）
        non_field_errors = error_detail.get('non_field_errors', [])
        first_error_msg = non_field_errors[0] if non_field_errors else '参数验证失败'
        error_data = error_detail
    else:
        # 其他类型的错误
        first_error_msg = str(error_detail)
        error_data = {"detail": str(error_detail)}

    logger.info(f"Validation error: {first_error_msg}")

    # 返回400状态码而不是200（验证错误应该是400）
    return Response({
        "code": 400,
        "message": first_error_msg,
        "data": error_data
    }, status=status.HTTP_200_OK)  # 改为400状态码


def format_permission_denied(e):
    """
    格式化 PermissionDenied 为统一响应结构
    """
    logger.info(f"Permission denied: {str(e)}")
    return Response({
        "code": 403,
        "message": str(e),
        "data": None
    }, status=status.HTTP_200_OK)

def format_http404_error(e):
    """
    格式化 ObjectDoesNotExist 为统一响应结构
    """
    logger.info(f"Object does not exist: {str(e)}")
    return Response({
        "code": 404,
        "message": "该数据不存在",
        "data": None
    })