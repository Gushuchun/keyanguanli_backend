from utils.base.baseModel import BaseModel
from django.db import models
import uuid

class Paper(BaseModel):
    id = models.AutoField(primary_key=True)
    sn = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    number = models.CharField(max_length=50, verbose_name='论文编号')
    title = models.CharField(max_length=200, verbose_name='论文标题')
    journal = models.CharField(max_length=100, verbose_name='期刊名称')
    publish_date = models.DateField(verbose_name='发表日期')
    abstract = models.TextField(verbose_name='摘要')
    keywords = models.CharField(max_length=200, verbose_name='关键词')
    file = models.CharField(max_length=255, verbose_name='论文文件')
    applicant_sn = models.UUIDField(verbose_name='申请人标识')
    applicant_name = models.CharField(max_length=50, verbose_name='申请人姓名')
    applicant_email = models.CharField(max_length=50, verbose_name='申请人邮箱')

    class Meta:
        verbose_name = '论文'
        verbose_name_plural = verbose_name
        db_table = 'paper'

class Author(BaseModel):
    id = models.AutoField(primary_key=True)
    sn = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    paper = models.UUIDField(max_length=100, verbose_name='论文的uuid')
    name = models.CharField('姓名', max_length=50)
    email = models.CharField('邮箱', max_length=20)
    phone = models.CharField('手机号', max_length=20)

    class Meta:
        verbose_name = '作者'
        verbose_name_plural = verbose_name
        db_table = 'paper_author'