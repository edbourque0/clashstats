from django import template
register = template.Library()
from django.db import models
from clanranking.models import Battles

@register.simple_tag
def get_combined_battles(member):
    team1_battles = member.team1tag.all()
    opponent1_battles = member.opponent1tag.all()
    combined_battles = team1_battles | opponent1_battles
    return combined_battles.order_by('-battleTime')

@register.simple_tag
def get_battle_stats(member):
    # Initialize a dictionary to hold the stats.
    stats = {}

    # Query all battles involving the member.
    involved_battles = Battles.objects.filter(
        models.Q(team1Tag=member) | 
        models.Q(team2Tag=member) | 
        models.Q(opponent1Tag=member) | 
        models.Q(opponent2Tag=member)
    ).distinct()

    for battle in involved_battles.order_by('-battleTime'):
        # Determine the opponent and whether the member won or lost.
        if battle.winner1Tag == member:
            opponent = battle.loser1Tag
            result = 'wins'
        else:
            opponent = battle.winner1Tag
            result = 'losses'
        
        opponent_name = opponent.name
        # Initialize opponent's stats in the dictionary if not already present.
        if opponent_name not in stats:
            # It seems the intention is to calculate expectation against opponent1Tag, but you might need to adjust based on actual opponent
            eloExp = 1 / (1 + 10 ** ((opponent.eloRating - member.eloRating) / 400))
            stats[opponent_name] = {'wins': 0, 'losses': 0, 'eloExpectation': round(eloExp * 100, 2)}
        
        # Increment the win or loss count.
        stats[opponent_name][result] += 1

    return stats
