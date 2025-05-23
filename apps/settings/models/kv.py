from utils.base.baseModel import BaseModel
from django.db import models

class KV(BaseModel):
    key = models.CharField(max_length=255, verbose_name='键')
    value = models.TextField(verbose_name='值')

    class Meta:
        db_table = 'kv'
        verbose_name = '设置表'
        verbose_name_plural = '设置表'