from collections import defaultdict

from celery import shared_task
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from apps.competition.models import Competition, StudentToCompetition, TeacherToCompetition
import logging

from apps.team.models import Team

logger = logging.getLogger('competition')

@shared_task
def clean_expired_competitions():
    now = datetime.now()
    warning_time = now - timedelta(hours=48)
    expiration_time = now - timedelta(hours=72)

    # 获取处于 pending 状态且在 48-72 小时之间创建的比赛
    warning_competitions = Competition.objects.filter(
        status='pending',
        create_time__lte=warning_time,
        create_time__gt=expiration_time,
        state=1,
        reminder_sent=False
    )

    # 发送提醒邮件
    for competition in warning_competitions:
        pending_students_relations = StudentToCompetition.objects.filter(
            competition=competition.sn,
            status='pending',
            state=1,
            reminder_sent=False
        )

        student_emails = [
            StudentToCompetition.get_email(rel.student) for rel in pending_students_relations
        ]

        pending_teachers_relations = TeacherToCompetition.objects.filter(
            competition=competition.sn,
            status='pending',
            state=1,
            reminder_sent=False
        )

        teacher_emails = [
            TeacherToCompetition.get_email(rel.teacher) for rel in pending_teachers_relations
        ]

        recipient_list = student_emails + teacher_emails

        if recipient_list:
            logger.info(f'发送邮件给 {recipient_list}')
            subject = '科研管理平台 竞赛确认提醒'
            message = f'您有待处理的竞赛申请：{competition.name}，请尽快确认！'
            from_email = settings.DEFAULT_FROM_EMAIL
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)

        pending_students_relations.update(reminder_sent=True)
        pending_teachers_relations.update(reminder_sent=True)
        competition.reminder_sent = True
        competition.save()

    # 获取超过72小时仍未确认的比赛并标记为 expired
    expired_competitions = Competition.objects.filter(
        status='pending',
        create_time__lte=expiration_time,
        state=1
    )

    for competition in expired_competitions:
        competition.status = 'expired'
        competition.save()
        logger.info(f'更新竞赛 {competition.name} 状态为过期')

        StudentToCompetition.objects.filter(
            competition=competition.sn,
            status='pending',
            state=1
        ).update(status='expired')

        TeacherToCompetition.objects.filter(
            competition=competition.sn,
            status='pending'
        ).update(status='expired')



@shared_task
def clean_expired_invite():
    now = datetime.now()
    warning_time = now - timedelta(hours=48)
    expiration_time = now - timedelta(hours=72)

    # 获取 48~72 小时之间的教师邀请（仅限关联的比赛为 confirmed 的情况）
    pending_teacher_invites = TeacherToCompetition.objects.filter(
        status='pending',
        reminder_sent=False,
        state=1,
        create_time__lte=warning_time,
        create_time__gt=expiration_time
    ).filter(team__in=Team.objects.filter(status='confirmed', state=1).values('sn'))

    # 发送提醒邮件
    email_group = defaultdict(list)
    competition_names = {}

    for invite in pending_teacher_invites:
        email = TeacherToCompetition.get_email(invite.teacher)
        if email:
            comp_obj = Competition.objects.get(sn=invite.competition, state=1)
            competition_names[invite.competition] = comp_obj.name
            email_group[invite.competition].append(email)

    # 遍历分组并发送邮件
    for comp_sn, recipients in email_group.items():
        comp_name = competition_names.get(comp_sn, "未知竞赛")
        message = f'您有来自竞赛（{comp_name}）的邀请，请尽快确认！'
        subject = '科研管理平台 竞赛邀请提醒'
        from_email = settings.DEFAULT_FROM_EMAIL
        logger.info(f'发送邮件给 {recipients}')
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipients,
            fail_silently=False,
        )

    # 更新这些邀请的 reminder_sent 字段
    pending_teacher_invites.update(reminder_sent=True)

    # 处理超过 72 小时的教师邀请
    expired_teacher_invites = TeacherToCompetition.objects.filter(
        status='pending',
        reminder_sent=True,
        state=1,
        create_time__lte=expiration_time
    ).filter(team__in=Team.objects.filter(status='confirmed', state=1).values('sn'))

    # 更新状态为 expired
    expired_teacher_invites.update(status='expired')


