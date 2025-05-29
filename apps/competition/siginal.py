from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Competition, TeacherToCompetition, StudentToCompetition
from apps.team.models import Team
from apps.student.models import Student

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

            confirm_exist = StudentToCompetition.objects.filter(
                competition=competition.sn,
            ).count()

            team = Team.objects.filter(sn=competition.team_sn).first()

            num = team.people_num - team.teacher_num

            if confirm_exist < num:
                return

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
                team = Team.objects.get(sn=competition.team_sn)
                team.race_num += 1
                colleges = []
                if competition.score != '无':
                    team.prize_num += 1
                    # 给每个学生的 race_num 和 prize_num 加 1
                    students = StudentToCompetition.objects.filter(competition=competition.sn)
                    for student in students:
                        student_obj = Student.objects.get(sn=student.student)
                        student_obj.race_num += 1
                        student_obj.prize_num += 1
                        student_obj.save()
                        # 获取学生对应的学院，并将学院的 prize_num 加 1
                        from apps.college.models import College
                        college = College.objects.filter(id=student_obj.college_id).first()
                        if college and college.id not in colleges:
                            college.prize_num += 1
                            college.save()
                            colleges.append(college.id)
                team.save()
