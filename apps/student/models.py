# users/models.py
from django.db import models
import uuid
from utils.BaseModel import BaseModel


class Student(BaseModel):
    GENDER_CHOICES = [(True, '男'), (False, '女')]

    id = models.AutoField(primary_key=True)
    sn = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    username = models.CharField('姓名',max_length=50, unique=True)
    gender = models.BooleanField('性别', choices=GENDER_CHOICES)
    college_id = models.IntegerField('学院id')
    cn = models.CharField('身份证', max_length=18, unique=True)
    phone = models.CharField('电话', max_length=20)
    team_id = models.CharField('团队id', max_length=100)
    prize_num = models.IntegerField('获奖总数', default=0)
    race_num = models.IntegerField('比赛总数', default=0)
    is_cap = models.BooleanField('队长', default=False)

    class Meta:
        app_label = 'student'
        db_table = 'student'
        verbose_name = '学生'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username