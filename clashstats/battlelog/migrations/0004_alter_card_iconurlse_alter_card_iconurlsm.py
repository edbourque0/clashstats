# Generated by Django 5.1.1 on 2024-10-29 02:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('battlelog', '0003_alter_playerinfo_legacytrophyroadhighscore'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='iconUrlse',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='card',
            name='iconUrlsm',
            field=models.CharField(max_length=100),
        ),
    ]
