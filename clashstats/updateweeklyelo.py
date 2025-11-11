from datetime import timedelta
from django.utils import timezone
from .models import Members, BattleLogs

def updateweeklyelo(battles):
    for battle in battles:
        """ Define common variables """
        winnerselo = (battle.winner1.weeklyelo + battle.winner2.weeklyelo) / 2
        loserselo = (battle.loser1.weeklyelo + battle.loser2.weeklyelo) / 2
        winnersexpectedscore = 1 / (1 + 10 ** ((loserselo - winnerselo) / 400))
        losersexpectedscore = 1 / (1 + 10 ** ((winnerselo - loserselo) / 400))

        """ Compute and update ELO of winners """
        w1newelo = battle.winner1.weeklyelo + 32 * (1 - winnersexpectedscore)
        w2newelo = battle.winner2.weeklyelo + 32 * (1 - winnersexpectedscore)
        Members.objects.filter(tag=battle.winner1.tag).update(weeklyelo=w1newelo)
        Members.objects.filter(tag=battle.winner2.tag).update(weeklyelo=w2newelo)

        """ Compute and update ELO of losers """
        l1newelo = battle.loser1.weeklyelo + 32 * (0 - losersexpectedscore)
        l2newelo = battle.loser2.weeklyelo + 32 * (0 - losersexpectedscore)
        Members.objects.filter(tag=battle.loser1.tag).update(weeklyelo=l1newelo)
        Members.objects.filter(tag=battle.loser2.tag).update(weeklyelo=l2newelo)