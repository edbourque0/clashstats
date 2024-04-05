from django.db import models

# Create your models here.

class Arena(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=100)

class GameMode(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=100)

class Clan(models.Model):
    tag = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    badgeId = models.PositiveIntegerField()

class Card(models.Model):
    id = models.CharField(max_length=15, primary_key=True)
    name = models.CharField(max_length=100)
    level = models.PositiveIntegerField()
    maxLevel = models.PositiveIntegerField()
    rarity = models.CharField(max_length=50)
    elixirCost = models.PositiveIntegerField(null=True, blank=True)
    iconUrlsm = models.CharField(max_length=50)
    iconUrlse = models.CharField(max_length=50)

class Player(models.Model):
    tag = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    crowns = models.PositiveIntegerField()
    kingTowerHitPoints = models.PositiveIntegerField()
    princessTower1HitPoints = models.PositiveIntegerField()
    princessTower2HitPoints = models.PositiveIntegerField()
    clan = models.ForeignKey(Clan, on_delete=models.SET_NULL, null=True, related_name='players')
    card1 = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True, related_name='card1')
    card2 = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True, related_name='card2')
    card3 = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True, related_name='card3')
    card4 = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True, related_name='card4')
    card5 = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True, related_name='card5')
    card6 = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True, related_name='card6')
    card7 = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True, related_name='card7')
    card8 = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True, related_name='card8')
    supportCards = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True, related_name='supportcard')
    elixirLeaked = models.FloatField()

class Battle(models.Model):
    battleTime = models.DateTimeField()
    type = models.CharField(max_length=100)
    isLadderTournament = models.CharField(max_length=5)
    arena = models.ForeignKey(Arena, on_delete=models.CASCADE)
    gameMode = models.ForeignKey(GameMode, on_delete=models.CASCADE)
    deckSelection = models.CharField(max_length=50)
    team = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='team_battles')
    opponent = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='opponent')
    isHostedMatch = models.CharField(max_length=5)
    leagueNumber = models.PositiveIntegerField(null=True, blank=True)
