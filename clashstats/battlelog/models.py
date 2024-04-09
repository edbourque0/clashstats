from django.db import models

# Create your models here.

class Arena(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=100, null=True, blank=True)

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
    @property
    def averageElixir(self):
        return round((self.card1.elixirCost + self.card2.elixirCost + self.card3.elixirCost + self.card4.elixirCost + self.card5.elixirCost + self.card6.elixirCost + self.card7.elixirCost + self.card8.elixirCost) / 8, 1)

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
    

class PlayerInfo(models.Model):
    tag = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=100)
    expLevel = models.IntegerField()
    trophies = models.IntegerField()
    bestTrophies = models.IntegerField()
    wins = models.IntegerField()
    losses = models.IntegerField()
    battleCount = models.IntegerField()
    threeCrownWins = models.IntegerField()
    challengeCardsWon = models.IntegerField()
    challengeMaxWins = models.IntegerField()
    tournamentCardsWon = models.IntegerField()
    tournamentBattleCount = models.IntegerField()
    role = models.CharField(max_length=50)
    donations = models.IntegerField()
    donationsReceived = models.IntegerField()
    totalDonations = models.IntegerField()
    warDayWins = models.IntegerField()
    clanCardsCollected = models.IntegerField()
    clan = models.ForeignKey(Clan, on_delete=models.SET_NULL, null=True)
    arena = models.ForeignKey(Arena, on_delete=models.SET_NULL, null=True)
    starPoints = models.IntegerField(null=True, blank=True)
    expPoints = models.IntegerField(null=True, blank=True)
    legacyTrophyRoadHighScore = models.IntegerField(null=True, blank=True)
    currentPathOfLegendSeasonResult = models.CharField(max_length=50, null=True, blank=True)
    lastPathOfLegendSeasonResult = models.CharField(max_length=50, null=True, blank=True)
    bestPathOfLegendSeasonResult = models.CharField(max_length=50, null=True, blank=True)
    totalExpPoints = models.IntegerField()
    
    def timespent(self):
        return (self.battleCount * 3)/60
    
    def timeratio(self):
        return round(self.trophies / self.timespent())
    
class Badge(models.Model):
    name = models.CharField(max_length=100)
    level = models.IntegerField()
    maxLevel = models.IntegerField()
    progress = models.IntegerField()
    target = models.IntegerField()
    iconUrls = models.CharField(max_length=150)
    @property
    def progressPerc(self):
        if self.target == 0:
            return 0
        else:
            return round((self.progress / self.target) * 100, 1)
    
class Achievement(models.Model):
    name = models.CharField(max_length=100)
    stars = models.IntegerField()
    value = models.IntegerField()
    target = models.IntegerField()
    info = models.CharField(max_length=150)
    completionInfo = models.CharField(max_length=150, null=True, blank=True)
    
class FavoriteCard(models.Model):
    name = models.CharField(max_length=100)
    id = models.CharField(max_length=15, primary_key=True)
    maxLevel = models.IntegerField()
    elixirCost = models.IntegerField()
    iconUrls = models.CharField(max_length=150)
    rarity = models.CharField(max_length=50)
