from collections import defaultdict

from celery import shared_task
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from apps.team.models import Team, StudentToTeam, TeacherToTeam
import logging

logger = logging.getLogger('team')

@shared_task
def clean_expired_teams():
    now = datetime.now()
    # 时间范围
    warning_time = now - timedelta(hours=48)
    expiration_time = now - timedelta(hours=72)

    # 48-72小时内的团队
    warning_teams = Team.objects.filter(
        status='pending',
        create_time__lte=warning_time,
        create_time__gt=expiration_time,
        state=1,
        reminder_sent=False
    )

    # 发送提醒邮件
    for team in warning_teams:
        pending_students_relations = StudentToTeam.objects.filter(
            team=team.sn,
            status='pending',
            state=1,
            reminder_sent=False
        )

        # 提取学生emails（使用 StudentToTeam.get_email）
        student_emails = [
            StudentToTeam.get_email(student_sn=rel.student)
            for rel in pending_students_relations
        ]

        pending_teachers_relations = TeacherToTeam.objects.filter(
            team=team.sn,
            status='pending',
            state=1,
            reminder_sent=False
        )

        # 假设 TeacherToTeam 也有类似 get_email 方法，否则需根据实际情况获取教师邮箱
        teacher_emails = [
            TeacherToTeam.get_email(teacher_sn=rel.teacher)
            for rel in pending_teachers_relations
        ]

        # 合并所有邮箱
        recipient_list = student_emails + teacher_emails

        # 发送邮件（需要实现get_email_for_user）
        if recipient_list:
            logger.info(f'发送提醒邮件给：{recipient_list}')
            subject = '科研管理平台 团队创建提醒'
            message = f'您有待处理的团队创建请求：团队 {team.name}，请尽快确认！'
            from_email = settings.DEFAULT_FROM_EMAIL
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=recipient_list,
                fail_silently=False,
            )

        pending_students_relations.update(reminder_sent=True)
        pending_teachers_relations.update(reminder_sent=True)

        team.reminder_sent = True
        team.save()

    # 超过72小时的团队
    expired_teams = Team.objects.filter(
        status='pending',
        create_time__lte=expiration_time,
        state=1,
    )

    # 更新过期团队及其成员
    for team in expired_teams:
        # 更新团队状态
        team.status = 'expired'
        team.save()

        logger.info(f'更新团队 {team.name} 状态为过期')
        # 更新未确认的成员状态
        StudentToTeam.objects.filter(
            team=team.sn,
            status='pending',
            state=1,
        ).update(status='expired')

        TeacherToTeam.objects.filter(
            team=team.sn,
            status='pending',
        ).update(status='expired')


@shared_task
def clean_expired_invite():
    now = datetime.now()
    warning_time = now - timedelta(hours=48)
    expiration_time = now - timedelta(hours=72)

    # 获取 48~72 小时之间的邀请（学生）
    pending_student_invites = StudentToTeam.objects.filter(
        status='pending',
        reminder_sent=False,
        state=1,
        create_time__lte=warning_time,
        create_time__gt=expiration_time
    ).filter(team__in=Team.objects.filter(status='confirmed', state=1).values('sn'))

    # 按团队分类学生邀请并发送邮件
    email_group = defaultdict(list)
    team_names = {}

    for invite in pending_student_invites:
        email = StudentToTeam.get_email(invite.student)
        if email:
            team_obj = Team.objects.get(sn=invite.team, state=1)
            team_names[invite.team] = team_obj.name
            email_group[invite.team].append(email)

    # 发送学生邀请邮件
    for team_sn, recipients in email_group.items():
        team_name = team_names.get(team_sn, "未知团队")
        message = f'您有来自团队（{team_name}）的邀请，请尽快确认！'
        send_mail(
            subject='科研管理平台 团队邀请提醒',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )
        StudentToTeam.objects.filter(team=team_sn, student__in=[StudentToTeam.objects.get(email=email).student for email in recipients]).update(reminder_sent=True)

    # 获取 48~72 小时之间的邀请（教师）
    pending_teacher_invites = TeacherToTeam.objects.filter(
        status='pending',
        reminder_sent=False,
        state=1,
        create_time__lte=warning_time,
        create_time__gt=expiration_time
    ).filter(team__in=Team.objects.filter(status='confirmed', state=1).values('sn'))

    # 按团队分类教师邀请并发送邮件
    teacher_email_group = defaultdict(list)
    teacher_team_names = {}

    for invite in pending_teacher_invites:
        email = TeacherToTeam.get_email(invite.teacher)
        if email:
            team_obj = Team.objects.get(sn=invite.team, state=1)
            teacher_team_names[invite.team] = team_obj.name
            teacher_email_group[invite.team].append(email)

    # 发送教师邀请邮件
    for team_sn, recipients in teacher_email_group.items():
        team_name = teacher_team_names.get(team_sn, "未知团队")
        message = f'您有来自团队（{team_name}）的邀请，请尽快确认！'
        send_mail(
            subject='科研管理平台 团队邀请提醒',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )
        TeacherToTeam.objects.filter(team=team_sn, teacher__in=[TeacherToTeam.objects.get(email=email).teacher for email in recipients]).update(reminder_sent=True)

    pending_student_invites.update(reminder_sent=True)
    pending_teacher_invites.update(reminder_sent=True)

    # 处理超过 72 小时的学生邀请
    expired_student_invites = StudentToTeam.objects.filter(
        status='pending',
        state=1,
        create_time__lte=expiration_time
    ).filter(team__in=Team.objects.filter(status='confirmed', state=1).values('sn'))
    expired_student_invites.update(status='expired')

    # 处理超过 72 小时的教师邀请
    expired_teacher_invites = TeacherToTeam.objects.filter(
        status='pending',
        state=1,
        create_time__lte=expiration_time
    ).filter(team__in=Team.objects.filter(status='confirmed', state=1).values('sn'))
    expired_teacher_invites.update(status='expired')

