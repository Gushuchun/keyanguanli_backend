from utils.base.baseModel import BaseModel
from django.db import models
import uuid

class Patent(BaseModel):
    id = models.AutoField(primary_key=True)
    sn = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    number = models.CharField(max_length=20, verbose_name='专利号')
    name = models.CharField(max_length=100, verbose_name='专利名称')
    date = models.DateField(verbose_name='申请日期')
    description = models.TextField(verbose_name='专利描述')
    patent_type = models.CharField(max_length=20, verbose_name='专利类型')
    applicant_name = models.CharField(max_length=50, verbose_name='申请人姓名')
    applicant_sn = models.UUIDField(default=uuid.uuid4, editable=False)
    applicant_phone = models.CharField(max_length=20, verbose_name='申请人手机号')
    applicant_email = models.CharField(max_length=20, verbose_name='申请人电子邮箱')
    file = models.CharField(max_length=255, verbose_name='证书文件')

    class Meta:
        app_label = 'patent'
        db_table = 'patent'
        verbose_name = '专利'
        verbose_name_plural = verbose_name

class Inventor(BaseModel):
    id = models.AutoField(primary_key=True)
    sn = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    patent = models.UUIDField(max_length=100, verbose_name='专利的uuid')
    name = models.CharField('姓名', max_length=50)
    phone = models.CharField('手机号', max_length=20)
    email = models.CharField('邮箱', max_length=20)

    class Meta:
        app_label = 'patent'
        db_table = 'patent_inventor'
        verbose_name = '发明人'
        verbose_name_plural = verbose_name
