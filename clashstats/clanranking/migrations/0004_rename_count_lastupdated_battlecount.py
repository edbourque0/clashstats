# Generated by Django 5.0.4 on 2024-04-11 23:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("clanranking", "0003_lastupdated"),
    ]

    operations = [
        migrations.RenameField(
            model_name="lastupdated",
            old_name="count",
            new_name="battleCount",
        ),
    ]
