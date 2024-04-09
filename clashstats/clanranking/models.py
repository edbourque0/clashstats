from django.db import models


class Clans(models.Model):
    tag = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    badgeId = models.PositiveIntegerField()
    clanScore = models.PositiveIntegerField()
    clanWarTrophies = models.PositiveIntegerField()
    requiredTrophies = models.PositiveIntegerField()
    donationsPerWeek = models.PositiveIntegerField()
    
class Members(models.Model):
    tag = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=50)
    lastSeen = models.DateTimeField()
    expLevel = models.PositiveIntegerField()
    trophies = models.PositiveIntegerField()
    arena = models.CharField(max_length=50, null=True)
    clanRank = models.PositiveIntegerField()
    clanChestPoints = models.PositiveIntegerField()
    clanPoints = models.PositiveIntegerField()
    wonBattles = models.PositiveIntegerField()
    lostBattles = models.PositiveIntegerField()
    def __str__(self):
        return self.tag
    
    def wlratio(self):
        if self.lostBattles == 0:
            return self.wonBattles
        else:
            return round(self.wonBattles/self.lostBattles, 1)
        
    def wgratio(self):
        if self.lostBattles == 0:
            return self.wonBattles
        else:
            return round(self.wonBattles/(self.wonBattles+self.lostBattles), 1)

    
class Battles(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    battleTime = models.DateTimeField()
    type = models.CharField(max_length=100)
    isLadderTournament = models.CharField(max_length=5)
    arena = models.CharField(max_length=50, null=True)
    gameMode = models.CharField(max_length=50)
    deckSelection = models.CharField(max_length=50)
    team1Tag = models.ForeignKey(Members, on_delete=models.SET_NULL, null=True, related_name='team1tag')
    team1Clan = models.ForeignKey(Clans, on_delete=models.SET_NULL, null=True, related_name='team1clan')
    team1Crowns = models.PositiveIntegerField()
    team2Tag = models.ForeignKey(Members, on_delete=models.SET_NULL, null=True, related_name='team2tag')
    team2Clan = models.ForeignKey(Clans, on_delete=models.SET_NULL, null=True, related_name='team2clan')
    team2Crowns = models.PositiveIntegerField(null=True)
    opponent1Tag = models.ForeignKey(Members, on_delete=models.SET_NULL, null=True, related_name='opponent1tag')
    opponent1Clan = models.ForeignKey(Clans, on_delete=models.SET_NULL, null=True, related_name='opponent1clan')
    opponent1Crowns = models.PositiveIntegerField()
    opponent2Tag = models.ForeignKey(Members, on_delete=models.SET_NULL, null=True, related_name='opponent2tag')
    opponent2Clan = models.ForeignKey(Clans, on_delete=models.SET_NULL, null=True, related_name='opponent2clan')
    opponent2Crowns = models.PositiveIntegerField(null=True)
    isHostedMatch = models.CharField(max_length=5)
    winner1Tag = models.ForeignKey(Members, on_delete=models.SET_NULL, null=True, related_name='winner1tag')
    loser1Tag = models.ForeignKey(Members, on_delete=models.SET_NULL, null=True, related_name='looser1tag')
