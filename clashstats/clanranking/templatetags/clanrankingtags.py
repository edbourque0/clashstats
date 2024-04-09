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

    for battle in involved_battles:
        # Determine the opponent and whether the member won or lost.
        if battle.winner1Tag == member:
            opponent = battle.loser1Tag.name
            result = 'wins'
        else:
            opponent = battle.winner1Tag.name
            result = 'losses'
        
        # Initialize opponent's stats in the dictionary if not already present.
        if opponent not in stats:
            stats[opponent] = {'wins': 0, 'losses': 0}
        
        # Increment the win or loss count.
        if opponent:
            stats[opponent][result] += 1

    return stats
