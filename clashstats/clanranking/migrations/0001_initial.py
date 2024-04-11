# Generated by Django 5.0.4 on 2024-04-09 04:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Clans",
            fields=[
                (
                    "tag",
                    models.CharField(max_length=20, primary_key=True, serialize=False),
                ),
                ("name", models.CharField(max_length=100)),
                ("type", models.CharField(max_length=50)),
                ("description", models.CharField(max_length=100)),
                ("badgeId", models.PositiveIntegerField()),
                ("clanScore", models.PositiveIntegerField()),
                ("clanWarTrophies", models.PositiveIntegerField()),
                ("requiredTrophies", models.PositiveIntegerField()),
                ("donationsPerWeek", models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="Members",
            fields=[
                (
                    "tag",
                    models.CharField(max_length=20, primary_key=True, serialize=False),
                ),
                ("name", models.CharField(max_length=100)),
                ("role", models.CharField(max_length=50)),
                ("lastSeen", models.DateTimeField()),
                ("expLevel", models.PositiveIntegerField()),
                ("trophies", models.PositiveIntegerField()),
                ("arena", models.CharField(max_length=50, null=True)),
                ("clanRank", models.PositiveIntegerField()),
                ("clanChestPoints", models.PositiveIntegerField()),
                ("clanPoints", models.PositiveIntegerField()),
                ("wonBattles", models.PositiveIntegerField()),
                ("lostBattles", models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="Battles",
            fields=[
                (
                    "id",
                    models.CharField(max_length=50, primary_key=True, serialize=False),
                ),
                ("battleTime", models.DateTimeField()),
                ("type", models.CharField(max_length=100)),
                ("isLadderTournament", models.CharField(max_length=5)),
                ("arena", models.CharField(max_length=50, null=True)),
                ("gameMode", models.CharField(max_length=50)),
                ("deckSelection", models.CharField(max_length=50)),
                ("team1Crowns", models.PositiveIntegerField()),
                ("team2Crowns", models.PositiveIntegerField(null=True)),
                ("opponent1Crowns", models.PositiveIntegerField()),
                ("opponent2Crowns", models.PositiveIntegerField(null=True)),
                ("isHostedMatch", models.CharField(max_length=5)),
                (
                    "opponent1Clan",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="opponent1clan",
                        to="clanranking.clans",
                    ),
                ),
                (
                    "opponent2Clan",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="opponent2clan",
                        to="clanranking.clans",
                    ),
                ),
                (
                    "team1Clan",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="team1clan",
                        to="clanranking.clans",
                    ),
                ),
                (
                    "team2Clan",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="team2clan",
                        to="clanranking.clans",
                    ),
                ),
                (
                    "loser1Tag",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="looser1tag",
                        to="clanranking.members",
                    ),
                ),
                (
                    "opponent1Tag",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="opponent1tag",
                        to="clanranking.members",
                    ),
                ),
                (
                    "opponent2Tag",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="opponent2tag",
                        to="clanranking.members",
                    ),
                ),
                (
                    "team1Tag",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="team1tag",
                        to="clanranking.members",
                    ),
                ),
                (
                    "team2Tag",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="team2tag",
                        to="clanranking.members",
                    ),
                ),
                (
                    "winner1Tag",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="winner1tag",
                        to="clanranking.members",
                    ),
                ),
            ],
        ),
    ]