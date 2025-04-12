from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Competition, TeacherToCompetition, StudentToCompetition
from apps.team.models import Team

@receiver(post_save, sender=StudentToCompetition)
@receiver(post_save, sender=TeacherToCompetition)
def update_competition_status(sender, instance, **kwargs):
    """
    检查所有老师和学生是否都已确认，如果是，则将比赛状态设为 confirmed
    """
    with transaction.atomic():
        # 从实例中获取比赛编号
        competition_sn = instance.competition
        competition = Competition.objects.select_for_update().get(sn=competition_sn)

        if competition.status != 'confirmed':
            unconfirmed_students = StudentToCompetition.objects.filter(
                competition=competition.sn,
                status='pending',
                is_cap=False
            ).exists()

            # 判断是否还有未确认老师
            unconfirmed_teachers = TeacherToCompetition.objects.filter(
                competition=competition.sn,
                status='pending',
            ).exists()


            if not (unconfirmed_students or unconfirmed_teachers):
                competition.status = 'confirmed'
                competition.save()
                team = Team.objects.get(sn=competition.team_id)
                team.race_num += 1
                if competition.score != '无':
                    team.prize_num += 1
                team.save()