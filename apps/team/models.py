# teams/user.py
from utils.base.baseModel import BaseModel
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
    status = models.CharField('团队状态', max_length=20, default='pending')
    reminder_sent = models.BooleanField('提醒是否已发送', default=False)

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


class StudentToTeam(BaseModel):
    STATUS_CHOICES = (
        ('pending', '待接受'),
        ('confirmed', '已接受'),
        ('rejected', '已拒绝'),
        ('expired', '已过期')
    )

    id = models.AutoField(primary_key=True)
    sn = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    student = models.UUIDField('学生sn', max_length=100)
    team = models.UUIDField('团队sn', max_length=100)
    is_cap = models.BooleanField('是否是队长', default=False)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    reminder_sent = models.BooleanField('提醒是否已发送', default=False)

    class Meta:
        app_label = 'team'
        db_table = 'student_to_team'
        verbose_name = '学生-团队表'
        verbose_name_plural = '学生-团队表'

    @classmethod
    def get_team_by_sn(cls, team_sn):
        return Team.objects.get(sn=team_sn, state=1)

    @classmethod
    def get_email(cls, student_sn):
        from apps.student.models import Student
        return Student.objects.get(sn=student_sn, state=1).email

class TeacherToTeam(BaseModel):
    STATUS_CHOICES = (
        ('pending', '待接受'),
        ('confirmed', '已接受'),
        ('rejected', '已拒绝'),
        ('expired', '已过期')
    )

    id = models.AutoField(primary_key=True)
    sn = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    teacher = models.UUIDField('老师sn', max_length=100)
    team = models.UUIDField('团队sn', max_length=100)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    reminder_sent = models.BooleanField('提醒是否已发送', default=False)

    class Meta:
        app_label = 'team'
        db_table = 'teacher_to_team'
        verbose_name = '老师-团队表'
        verbose_name_plural = '老师-团队表'

    @classmethod
    def get_email(cls, teacher_sn):
        from apps.teacher.models import Teacher
        return Teacher.objects.get(sn=teacher_sn, state=1).email
