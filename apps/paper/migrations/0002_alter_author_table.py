# Generated by Django 5.1.2 on 2025-05-31 12:51

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("paper", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelTable(
            name="author",
            table="paper_author",
        ),
    ]
