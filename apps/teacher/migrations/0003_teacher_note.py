# Generated by Django 5.1.2 on 2025-05-10 00:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("teacher", "0002_teacher_avatar"),
    ]

    operations = [
        migrations.AddField(
            model_name="teacher",
            name="note",
            field=models.CharField(blank=True, max_length=255, verbose_name="备注"),
        ),
    ]
