# teams/models.py
from django.db import models
from utils.baseModel import BaseModel
import uuid
from apps.teacher.models import Teacher
from django.db import models, transaction

class Team(BaseModel):
    id = models.AutoField(primary_key=True)
    sn = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField('团队名称', max_length=100)
    race_num = models.IntegerField('比赛数', default=0)
    prize_num = models.IntegerField('获奖数', default=0)
    people_num = models.IntegerField('总人数', default=0)
    cap = models.UUIDField('队长sn', max_length=100)
    teacher_num = models.IntegerField('老师人数', default=0)

    class Meta:
        app_label = 'team'
        db_table = 'team'
        verbose_name = '团队'
        verbose_name_plural = '团队'
        ordering = ['-create_time']

    def __str__(self):
        return self.name

    @classmethod
    def get_teacher_name(cls, teacher_sn):
        return Teacher.objects.get(sn=teacher_sn).username

    def delete(self, using=None, keep_parents=False):
        """
        重写delete方法实现软删除：
        1. 将团队state设为0
        2. 更新所有关联的TeacherToTeam和StudentToTeam记录state=0
        3. 记录解散时间
        """
        with transaction.atomic():
            # 更新团队状态
            self.state = 0
            self.save()

            # 更新教师关联表
            TeacherToTeam.objects.filter(team=self.sn).update(state=0)

            # 更新学生关联表
            StudentToTeam.objects.filter(team=self.sn).update(state=0)

    def hard_delete(self):
        """真实删除方法"""
        super().delete()


class TeamInvite(BaseModel):
    STATUS_CHOICES = (
        ('0', '待接受'),
        ('1', '已接受'),
        ('2', '已拒绝'),
    )
    id = models.AutoField(primary_key=True)
    sn = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    team = models.CharField('团队sn', max_length=100, blank=True, null=True)
    member_id = models.UUIDField('成员sn', max_length=100, blank=True, null=True)
    cap = models.UUIDField('队长sn', max_length=100)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    teacher = models.UUIDField('老师sn', max_length=100, blank=True, null=True)

    class Meta:
        app_label = 'team'
        db_table = 'team_invite'
        verbose_name = '团队邀请表'
        verbose_name_plural = '团队邀请表'

    @classmethod
    def name(cls, id):
        return Team.objects.get(id=id).name


class StudentToTeam(BaseModel):
    id = models.AutoField(primary_key=True)
    sn = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    student = models.UUIDField('学生sn', max_length=100)
    team = models.UUIDField('团队sn', max_length=100)
    is_cap = models.BooleanField('是否是队长', default=False)

    class Meta:
        app_label = 'team'
        db_table = 'student_to_team'
        verbose_name = '学生-团队表'
        verbose_name_plural = '学生-团队表'

    @classmethod
    def get_team_by_sn(cls, team_sn):
        return Team.objects.get(sn=team_sn, state=1)

class TeacherToTeam(BaseModel):
    id = models.AutoField(primary_key=True)
    sn = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    teacher = models.UUIDField('老师sn', max_length=100)
    team = models.UUIDField('团队sn', max_length=100)

    class Meta:
        app_label = 'team'
        db_table = 'teacher_to_team'
        verbose_name = '老师-团队表'
        verbose_name_plural = '老师-团队表'