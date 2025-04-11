from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Team, StudentToTeam, TeacherToTeam
from apps.team.models import Team


@receiver(post_save, sender=StudentToTeam)
@receiver(post_save, sender=TeacherToTeam)
def update_competition_status(sender, instance, **kwargs):
    """
    检查所有老师和学生是否都已确认，如果是，则将比赛状态设为 confirmed
    同时更新团队的人数统计(people_num和teacher_num)
    """
    with transaction.atomic():
        # 从实例中获取比赛编号
        team_sn = instance.competition
        team = Team.objects.select_for_update().get(sn=team_sn)

        # 检查是否还有未确认的学生
        unconfirmed_students = StudentToTeam.objects.filter(
            team=team.sn,
            status='pending',
            is_cap=False
        ).exists()

        # 检查是否还有未确认的老师
        unconfirmed_teachers = TeacherToTeam.objects.filter(
            competition=team.sn,
            status='pending',
        ).exists()

        # 如果没有未确认的人员
        if not (unconfirmed_students or unconfirmed_teachers):
            # 获取已确认学生数量
            confirmed_students_count = StudentToTeam.objects.filter(
                team=team.sn,
                status='confirmed'
            ).count()

            # 获取已确认老师数量
            confirmed_teachers_count = TeacherToTeam.objects.filter(
                competition=team.sn,
                status='confirmed'
            ).count()

            # 更新团队状态和人数统计
            team.state = 1
            team.people_num = confirmed_students_count  # 更新学生人数
            team.teacher_num = confirmed_teachers_count  # 更新老师人数
            team.save()