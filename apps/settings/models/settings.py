from utils.base.baseModel import BaseModel
from django.db import models

class UserSettings(BaseModel):
    username = models.CharField(max_length=255, verbose_name='用户名')
    sn = models.CharField(max_length=255, verbose_name='sn')
    send_email = models.BooleanField(verbose_name='是否发送邮件', default=True)
    cursor = models.BooleanField(verbose_name='是否使用系统光标', default=True)

    class Meta:
        db_table = 'settings'
        verbose_name = '用户设置表'
        verbose_name_plural = '用户设置表'