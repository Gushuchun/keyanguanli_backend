# Generated by Django 5.1.2 on 2025-05-13 22:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0003_smscode"),
    ]

    operations = [
        migrations.CreateModel(
            name="LoginLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "create_time",
                    models.DateTimeField(
                        auto_now_add=True, null=True, verbose_name="创建时间"
                    ),
                ),
                (
                    "update_time",
                    models.DateTimeField(auto_now=True, null=True, verbose_name="更新时间"),
                ),
                (
                    "state",
                    models.CharField(
                        choices=[("1", "正常"), ("0", "停用")],
                        default="1",
                        max_length=1,
                        verbose_name="数据状态",
                    ),
                ),
                ("user", models.CharField(max_length=255, verbose_name="用户")),
                (
                    "method",
                    models.CharField(
                        choices=[("email", "邮箱"), ("password", "密码")],
                        max_length=10,
                        verbose_name="登录方式",
                    ),
                ),
                ("status", models.CharField(max_length=255, verbose_name="是否登陆成功")),
                ("ip", models.CharField(max_length=32, verbose_name="IP地址")),
                ("location", models.CharField(max_length=64, verbose_name="位置")),
            ],
            options={
                "verbose_name": "登录日志",
                "verbose_name_plural": "登录日志",
                "db_table": "login_log",
            },
        ),
    ]
