import uuid

from django.db import models, transaction


class BaseModel(models.Model):
    STATE_CHOICE = (
        ('1', '正常'), ('0', '停用')
    )
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name='更新时间')
    state = models.CharField(max_length=1, verbose_name="数据状态", choices=STATE_CHOICE, default='1')

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """重写delete方法实现软删除"""
        with transaction.atomic():
            self.state = 0
            self.save()

    def hard_delete(self):
        """真实删除方法"""
        super().delete()



class BaseIdModel(BaseModel):
    id = models.AutoField(primary_key=True, verbose_name="id")

    class Meta:
        abstract = True


class BaseUuidModel(BaseModel):
    code = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='编码')

    class Meta:
        abstract = True
