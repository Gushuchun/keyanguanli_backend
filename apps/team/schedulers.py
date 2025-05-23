import logging
import os
from .tasks import clean_expired_teams, clean_expired_invite

logger = logging.getLogger('team')

def start_scheduler():
    from apscheduler.schedulers.background import BackgroundScheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(clean_expired_teams, 'cron', id='clean_expired_teams', hour='*/1', max_instances=1)
    scheduler.add_job(clean_expired_invite, 'cron', id='clean_expired_invite', hour='*/1', max_instances=1)

    scheduler.start()
    logger.info('过期团队创建清理定时任务开始运行')
    logger.info('过期团队邀请清理定时任务开始运行')