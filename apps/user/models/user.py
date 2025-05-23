from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from cryptography.fernet import Fernet
from django.conf import settings

FERNET_KEY = settings.FERNET_KEY  # 假设密钥存在于 settings.py 文件中
cipher = Fernet(FERNET_KEY)



class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, role='student'):
        """
        Creates and saves a User with the given email
        """
        user = self.model(
            username=username,
            role=role,
        )
        if email:
            user.email = UserManager.normalize_email(email) or None

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, ):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            username=username,
            email=email,
            password=password,
        )

        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def get_or_create_user(self, username, email=None, password=None):
        # 根据用户名和邮箱查找
        user = self.model.objects.filter(username=username).first()

        if user is None and email:
            user = self.model.objects.filter(email=email).first()

        # 找不到就创建一个新的
        if not user:
            user = self.create_user(username=username, email=email, password=password)
            created = True
        else:
            created = False

        return user, created


class UserModel(AbstractUser):
    GENDER_CHOICES = (
        ('M', '男'),
        ('F', '女'),
    )
    # code = models.UUIDField(default=uuid.uuid4, verbose_name='唯一编码', unique=True)
    cn = models.CharField(max_length=128, verbose_name="中文姓名")
    email = models.EmailField(default=None, blank=True, null=True, verbose_name='邮箱')
    tel = models.CharField(max_length=32, null=True, blank=True, verbose_name="手机号", )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True, verbose_name="性别", )
    role = models.CharField(max_length=32, verbose_name="角色", default='student')

    objects = UserManager()

    # USERNAME_FIELD = 'tel'

    class Meta:
        db_table = 'user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        app_label = 'user'

    def __str__(self):
        return self.cn or self.username

    @property
    def is_admin(self):
        if self.is_staff or self.is_superuser:
            return True
        return False

    def set_cn(self, value):
        """加密身份证号"""
        self.cn = cipher.encrypt(value.encode()).decode()

    def get_cn(self):
        """解密身份证号"""
        return cipher.decrypt(self.cn.encode()).decode()

    # 在保存模型之前自动加密身份证号
    def save(self, *args, **kwargs):
        if self.cn:
            self.set_cn(self.cn)  # 自动加密 cn 字段
        super().save(*args, **kwargs)


