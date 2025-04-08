# users/models.py
from django.db import models
import uuid
from utils.BaseModel import BaseModel
from cryptography.fernet import Fernet
from django.conf import settings

FERNET_KEY = settings.FERNET_KEY  # 假设密钥存在于 settings.py 文件中
cipher = Fernet(FERNET_KEY)

class Student(BaseModel):
    GENDER_CHOICES = [(True, '男'), (False, '女')]

    id = models.AutoField(primary_key=True)
    sn = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    username = models.CharField('姓名',max_length=50, unique=True)
    gender = models.BooleanField('性别', choices=GENDER_CHOICES)
    college_id = models.IntegerField('学院id')
    cn = models.CharField('身份证', max_length=250,)
    phone = models.CharField('电话', max_length=20)
    prize_num = models.IntegerField('获奖总数', default=0)
    race_num = models.IntegerField('比赛总数', default=0)
    # is_cap = models.BooleanField('是否是队长', default=False)
    email = models.CharField('邮箱', blank=True, max_length=100)

    class Meta:
        app_label = 'student'
        db_table = 'student'
        verbose_name = '学生'
        verbose_name_plural = verbose_name
    def set_cn(self, value):
        """加密身份证号"""
        self.cn = cipher.encrypt(value.encode()).decode()

    def get_cn(self):
        """解密身份证号"""
        cn = cipher.decrypt(self.cn.encode()).decode()
        return cipher.decrypt(self.cn.encode()).decode()

    # 在保存模型之前自动加密身份证号
    # def save(self, *args, **kwargs):
    #     if self.cn:
    #         self.set_cn(self.cn)  # 自动加密 cn 字段
    #     super().save(*args, **kwargs)

    def __str__(self):
        return self.username