from django.db import models, transaction
import uuid

from apps.team.models import Team
from utils.baseModel import BaseModel


class Competition(BaseModel):
    STATUS_CHOICES = [
        ('pending', '待确认'),
        ('confirmed', '已确认'),
    ]

    id = models.AutoField(primary_key=True)
    sn = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField('比赛名称', max_length=100)
    date = models.DateField('比赛日期')
    description = models.CharField('比赛描述', max_length=1000)
    score = models.CharField('比赛成绩', max_length=100)
    teacher_num = models.IntegerField('老师数量', default=0)
    team_id = models.UUIDField('团队的uuid', max_length=100, blank=True, null=True)
    file = models.CharField("证书图片地址", max_length=255)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    note = models.TextField('备注', blank=True, null=True)

    class Meta:
        app_label = 'competition'
        db_table = 'competition'
        verbose_name = '比赛'
        verbose_name_plural = verbose_name

    def delete(self, using=None, keep_parents=False):
        """重写delete方法实现软删除"""
        with transaction.atomic():
            self.state = 0
            self.save()

            team = Team.objects.filter(sn=self.team_id).first()
            team.race_num -=1
            if self.score != '无':
                team.prize_num -=1
            team.save()

            # 标记所有成员确认记录为已删除
            CompetitionMemberConfirm.objects.filter(sn=self.sn).update(state=0)

    def hard_delete(self):
        """真实删除方法"""
        super().delete()

    @classmethod
    def get_cap(cls, id):
        competition = cls.objects.filter(id=id).first()
        if competition:
            team = Team.objects.filter(sn=competition.team_id).first()
            if team:
                return team.cap
        return None

class CompetitionMemberConfirm(BaseModel):
    STATUS_CHOICES = [
        ('pending', '待确认'),
        ('confirmed', '已确认'),
    ]

    id = models.AutoField(primary_key=True)
    sn = models.UUIDField("比赛的uuid", max_length=100)
    student = models.UUIDField('学生的uuid', max_length=100, blank=True, null=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending', blank=True, null=True)
    note = models.TextField('备注', blank=True, null=True)
    teacher = models.UUIDField('带队老师', max_length=100, blank=True, null=True)
    is_cap = models.BooleanField('是否是队长', default=False)

    class Meta:
        app_label = 'competition'
        db_table = 'competition_member_confirmation'
        verbose_name = '成员确认'
        verbose_name_plural = verbose_name

