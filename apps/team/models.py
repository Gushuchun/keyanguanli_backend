# teams/models.py
from django.db import models
from utils.BaseModel import BaseModel
import uuid

class Team(BaseModel):
    id = models.AutoField(primary_key=True)
    sn = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField('团队名称', max_length=100)
    race_num = models.IntegerField('比赛数', default=0)
    prize_num = models.IntegerField('获奖数', default=0)
    people_num = models.IntegerField('人数', default=0)

    class Meta:
        app_label = 'team'
        db_table = 'team'
        verbose_name = '团队'
        verbose_name_plural = '团队'

    def __str__(self):
        return self.name