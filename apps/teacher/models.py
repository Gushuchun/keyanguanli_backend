# teachers/models.py
from django.db import models
import uuid
from utils.base.baseModel import BaseModel


class Teacher(BaseModel):
    GENDER_CHOICES = [
        (True, '男'),
        (False, '女')
    ]

    TITLE_CHOICES = [
        ('professor', '教授'),
        ('associate_professor', '副教授'),
        ('lecturer', '讲师'),
        ('assistant', '助教')
    ]

    id = models.AutoField(primary_key=True)
    sn = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    username = models.CharField('姓名', max_length=50)
    gender = models.BooleanField('性别', choices=GENDER_CHOICES, default=True)
    college_id = models.CharField('学院id', max_length=100)
    phone = models.CharField('电话', max_length=20, blank=True)
    email = models.EmailField('邮箱', blank=True)
    title = models.CharField('职称', max_length=50, choices=TITLE_CHOICES)
    is_active = models.BooleanField('在职状态', default=True)

    class Meta:
        app_label = "teacher"
        db_table = "teacher"
        verbose_name = "教师信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.name}({self.get_title_display()})"