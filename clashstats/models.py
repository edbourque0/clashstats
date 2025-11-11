import uuid
from django.db import models
from django.db.models import CASCADE
from django.utils import timezone

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
    elo = models.PositiveIntegerField(null=False, default=1000)
    weeklyelo = models.PositiveIntegerField(null=False, default=1000)

class BattleLogs(models.Model):
    id = models.CharField(primary_key=True, editable=False)
    type = models.CharField(max_length=50)
    battleTime = models.DateTimeField()
    gameMode = models.CharField(max_length=25)
    winner1 = models.ForeignKey(Members, on_delete=models.CASCADE, null=False, related_name='winner12member')
    winner2 = models.ForeignKey(Members, on_delete=models.CASCADE, null=False, related_name='winner22member')
    loser1 = models.ForeignKey(Members, on_delete=models.CASCADE, null=False, related_name='loser12member')
    loser2 = models.ForeignKey(Members, on_delete=models.CASCADE, null=False, related_name='loser22member')
    elocalculated = models.BooleanField(null=False, default=False)
    weeklyelocalculated = models.DateTimeField(null=False, default=timezone.now())

class Refresh(models.Model):
    id = models.UUIDField(primary_key=True, null=False, default=uuid.uuid4())
    timestamp = models.DateTimeField(null=False, default=timezone.now())
    clanTag = models.ForeignKey(Clans, on_delete=models.CASCADE, null=False, related_name='refresh2clan')
    source = models.CharField(null=False, default='api')