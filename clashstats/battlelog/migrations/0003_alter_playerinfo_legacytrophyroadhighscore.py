# Generated by Django 5.0.4 on 2024-04-08 23:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("battlelog", "0002_alter_arena_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="playerinfo",
            name="legacyTrophyRoadHighScore",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]