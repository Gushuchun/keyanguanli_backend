from celery import shared_task
from django.core.mail import send_mail
import logging

logger = logging.getLogger('user')

@shared_task
def send_email_async(subject, message, from_email, recipient_list):
    try:
        send_mail(subject=subject,
                  message=message,
                  from_email=from_email,
                  recipient_list=recipient_list,
                  fail_silently=False)
        logger.info(f"发送邮件成功: {recipient_list}, 主题: {subject}")
        return True
    except Exception as e:
        logger.error(f"发送邮件失败: {e}")
        return False