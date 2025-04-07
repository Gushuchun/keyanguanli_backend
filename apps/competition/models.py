from django.db import models
import uuid
from utils.BaseModel import BaseModel


class Competition(BaseModel):
    STATUS_CHOICES = [
        ('pending', '待确认'),
        ('confirmed', '已确认'),
    ]

    id = models.AutoField(primary_key=True)
    sn = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    date = models.DateField('比赛日期')
    description = models.CharField('比赛描述', max_length=255)
    score = models.CharField('比赛成绩', max_length=100)
    teacher = models.CharField('带队老师', max_length=50)
    team_id = models.CharField('团队的uuid', max_length=100)
    file = models.FileField('证书图片', upload_to='competitions/')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        app_label = 'competition'
        db_table = 'competition'
        verbose_name = '比赛'
        verbose_name_plural = verbose_name


class CompetitionMemberConfirm(models.Model):
    STATUS_CHOICES = [
        ('pending', '待确认'),
        ('confirmed', '已确认'),
    ]

    id = models.AutoField(primary_key=True)
    sn = models.ForeignKey(Competition, to_field='sn', on_delete=models.CASCADE, verbose_name='比赛')
    student = models.CharField('学生的uuid', max_length=100)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        app_label = 'competition'
        db_table = 'competition_member_confirmation'
        verbose_name = '成员确认'
        verbose_name_plural = verbose_name

