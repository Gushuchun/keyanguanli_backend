from utils.base.baseModel import BaseModel
from django.db import models

class SMSCode(BaseModel):
    email = models.EmailField(verbose_name='邮箱')
    code = models.CharField(max_length=6, verbose_name='验证码')

    class Meta:
        db_table = 'sms_code'
        verbose_name = '短信验证码'
        verbose_name_plural = verbose_name
        app_label = 'user'


class LoginLog(BaseModel):
    LOGIN_METHOD_CHOICES = (
        ('email', '邮箱'),
        ('password', '密码'),
    )
    user = models.CharField(max_length=255, verbose_name='用户')
    method = models.CharField(max_length=10, choices=LOGIN_METHOD_CHOICES, verbose_name='登录方式')
    status = models.CharField(max_length=255, verbose_name='是否登陆成功')
    ip = models.CharField(max_length=255, verbose_name='IP地址')
    location = models.CharField(max_length=255, verbose_name='位置')

    class Meta:
        db_table = 'login_log'
        verbose_name = '登录日志'
        verbose_name_plural = verbose_name
        app_label = 'user'
