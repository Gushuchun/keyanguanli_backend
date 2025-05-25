from django.core.management.base import BaseCommand
from apps.college.models import College

class Command(BaseCommand):
    help = '初始化学院信息'

    def handle(self, *args, **options):
        colleges = [
            '计算机科学与工程学院',
            '商学院',
            '机械与能源工程学院',
            '食品科学与工程学院',
            '材料科学与工程学院',
            '人文与教育学院'
        ]

        for college_name in colleges:
            College.objects.get_or_create(name=college_name)

        self.stdout.write(self.style.SUCCESS('成功初始化学院信息'))