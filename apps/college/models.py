from utils.base.baseModel import BaseModel
from django.db import models

class College(BaseModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField('学院名称', max_length=100, unique=True)
    prize_num = models.IntegerField('获奖总数', default=0)
    paper_num = models.IntegerField('论文总数', default=0)
    patent_num = models.IntegerField('专利总数', default=0)

    class Meta:
        app_label = 'college'
        db_table = 'college'
        verbose_name = '成员确认'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name