# Generated by Django 5.1.2 on 2025-04-12 03:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("team", "0002_delete_teaminvite"),
    ]

    operations = [
        migrations.AlterField(
            model_name="studenttoteam",
            name="status",
            field=models.CharField(
                choices=[("pending", "待接受"), ("confirmed", "已接受"), ("rejected", "已拒绝")],
                default="pending",
                max_length=20,
                verbose_name="状态",
            ),
        ),
    ]
