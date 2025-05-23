from django.core.management.base import BaseCommand
from apps.student.models import Student
from apps.teacher.models import Teacher
from apps.settings.models import UserSettings

class Command(BaseCommand):
    help = 'Create UserSettings for all existing users'

    def handle(self, *args, **kwargs):
        created_count = 0

        for student in Student.objects.all():
            if not UserSettings.objects.filter(username=student.username).exists():
                UserSettings.objects.create(
                    username=student.username,
                    sn=student.sn,
                    send_email=True,
                    cursor=True
                )
                created_count += 1

        for teacher in Teacher.objects.all():
            if not UserSettings.objects.filter(username=teacher.username).exists():
                UserSettings.objects.create(
                    username=teacher.username,
                    sn=teacher.sn,
                    send_email=True,
                    cursor=True
                )
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'成功在用户设置表中创建了 {created_count} 条记录。'
        ))
