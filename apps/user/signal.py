# signals.py
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.utils import timezone
from .models import LoginLog
from utils.service.geo import get_location
import logging

logger = logging.getLogger(__name__)

@receiver(user_logged_in)
def handle_login_success(sender, request, user, **kwargs):
    """登录成功触发器（支持密码和验证码登录）"""
    # 通过 request 属性判断登录方式
    method = getattr(request, 'login_method', 'password')  # 默认为密码登录

    # 更新最后登录时间
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])

    # 获取 IP 和地理位置
    ip_address = request.META.get('REMOTE_ADDR', 'unknown')
    location = get_location(ip_address)

    # 记录日志
    LoginLog.objects.create(
        user=user.username,
        method=method,  # 动态设置登录方式
        status=1,
        ip=ip_address,
        location=location
    )
    logger.info(f'用户 {user.username} 通过 {method} 登录成功')

@receiver(user_login_failed)
def handle_login_failed(sender, credentials, request, **kwargs):
    """登录失败触发器（支持邮箱和用户名）"""
    # 优先从 credentials 获取邮箱，其次用户名
    username = credentials.get('email') or credentials.get('username', 'unknown')

    # 获取 IP
    ip_address = 'unknown'
    if request is not None:
        ip_address = request.META.get('REMOTE_ADDR', 'unknown')

    # 获取地理位置
    location = get_location(ip_address)

    # 记录日志
    LoginLog.objects.create(
        user=username,
        method='email' if 'email' in credentials else 'password',
        status=0,
        ip=ip_address,
        location=location
    )
    logger.warning(f'登录失败尝试: {username}（IP: {ip_address}）')