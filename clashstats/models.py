from django.db import models
import requests
from django.db.models import CASCADE
import uuid


# Create your models here.

class Clans(models.Model):
    tag = models.CharField(max_length=12, primary_key=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20)
    badgeId = models.PositiveIntegerField()
    location = models.CharField(max_length=3)
    donationsPerWeek = models.PositiveIntegerField()
    members = models.PositiveIntegerField()

class Members(models.Model):
    tag = models.CharField(max_length=12, primary_key=True)
    clanTag = models.ForeignKey(Clans, on_delete=models.CASCADE, null=True, related_name='clanTag')
    name = models.CharField(max_length=50)
    role = models.CharField(max_length=10)
    lastSeen = models.DateTimeField()
    expLevel = models.PositiveIntegerField()
    trophies = models.PositiveIntegerField()
    clanRank = models.PositiveIntegerField()
    donations = models.PositiveIntegerField()
    donationsReceived = models.PositiveIntegerField()
    elo = models.PositiveIntegerField(null=True)

class BattleLogs(models.Model):
    id = models.CharField(primary_key=True, editable=False)
    type = models.CharField(max_length=50)
    battleTime = models.DateTimeField()
    gameMode = models.CharField(max_length=25)
    winner1 = models.ForeignKey(Members, on_delete=models.CASCADE, null=False, related_name='winner12member')
    winner2 = models.ForeignKey(Members, on_delete=models.CASCADE, null=False, related_name='winner22member')
    loser1 = models.ForeignKey(Members, on_delete=models.CASCADE, null=False, related_name='loser12member')
    loser2 = models.ForeignKey(Members, on_delete=models.CASCADE, null=False, related_name='loser22member')