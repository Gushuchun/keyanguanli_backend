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
        team_sn = instance.team
        team = Team.objects.select_for_update().get(sn=team_sn)

        # confirm_exist = StudentToTeam.objects.filter(
        #     team=team.sn,
        # ).count()
        #
        # num = team.people_num - team.teacher_num
        #
        # if confirm_exist != num:
        #     return

        # 检查是否还有未确认的学生
        unconfirmed_students = StudentToTeam.objects.filter(
            team=team.sn,
            status='pending',
            # is_cap=False
        ).exists()

        unconfirmed_students_2 = StudentToTeam.objects.filter(
            team=team.sn,
            status='confirmed',
        ).count()
        if unconfirmed_students_2 == 1 :
            return


        # 检查是否还有未确认的老师
        unconfirmed_teachers = TeacherToTeam.objects.filter(
            team=team.sn,
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
                team=team.sn,
                status='confirmed'
            ).count()

            # 更新团队状态和人数统计
            team.status = 'confirmed'
            team.people_num = confirmed_students_count + confirmed_teachers_count
            team.teacher_num = confirmed_teachers_count
            team.save()