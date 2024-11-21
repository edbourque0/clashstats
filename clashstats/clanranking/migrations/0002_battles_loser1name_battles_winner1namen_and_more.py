# Generated by Django 5.1.1 on 2024-11-21 01:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clanranking', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='battles',
            name='loser1Name',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='battles',
            name='winner1Namen',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='battles',
            name='loser1Tag',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='loser1tag', to='clanranking.members'),
        ),
    ]