from django import template
from django.utils import timezone
register = template.Library()
from django.db import models
from clanranking.models import Battles, Members, weeklyRanking
from datetime import timedelta, datetime


@register.simple_tag
def get_combined_battles(member):
    team1_battles = member.team1tag.all()
    opponent1_battles = member.opponent1tag.all()
    combined_battles = team1_battles | opponent1_battles
    return combined_battles.order_by("-battleTime")


@register.simple_tag
def get_battle_stats(member):
    # Initialize a dictionary to hold the stats for each member.
    all_members = Members.objects.exclude(tag=member.tag)
    stats = {
        other_member.name: {
            "wins": 0,
            "losses": 0,
            "eloExpectation": round(1 / (1 + 10 ** ((other_member.eloRating - member.eloRating) / 400)) * 100)
        }
        for other_member in all_members
    }

    # Query all battles involving the member.
    involved_battles = Battles.objects.filter(
        models.Q(team1Tag=member) |
        models.Q(team2Tag=member) |
        models.Q(opponent1Tag=member) |
        models.Q(opponent2Tag=member)
    ).distinct()

    for battle in involved_battles.order_by("-battleTime"):
        # Determine the opponent and whether the member won or lost.
        if battle.winner1Tag == member:
            opponent = battle.loser1Tag
            result = "wins"
        else:
            opponent = battle.winner1Tag
            result = "losses"

        # Use opponent's name to update stats.
        if opponent.name in stats:
            stats[opponent.name][result] += 1

    # Sort the dictionary by wins in descending order
    sorted_stats = dict(sorted(stats.items(), key=lambda item: item[1]['eloExpectation'], reverse=True))

    return sorted_stats


@register.simple_tag
def get_weekly_ranking(week_start=datetime.now() - timedelta(weeks=1), week_end=datetime.now()):
    weeklyRanking.objects.all().delete()
    for member in Members.objects.all():
        weeklyRanking.objects.create(tag=Members.objects.filter(tag=member.tag).get())

    for battle in Battles.objects.filter(battleTime__range=[week_start, week_end]):
        expectation_t = 1 / (1 + 10 ** ((battle.opponent1Tag.eloRating - battle.team1Tag.eloRating) / 400))
        expectation_o = 1 - expectation_t
        sAt = 1 if battle.team1Tag == battle.winner1Tag else 0
        sAo = 1 if battle.opponent1Tag == battle.winner1Tag else 0
        newRanking_t = battle.team1Tag.eloRating + 32 * (sAt - expectation_t)
        newRanking_o = battle.opponent1Tag.eloRating + 32 * (sAo - expectation_o)
        weeklyRanking.objects.filter(tag=battle.team1Tag.tag).update(eloRating=newRanking_t)
        weeklyRanking.objects.filter(tag=battle.opponent1Tag.tag).update(eloRating=newRanking_o)

    mem_dict = {}
    for index, member in enumerate(weeklyRanking.objects.filter(~models.Q(eloRating=1000)).order_by('-eloRating')):
        mem_dict[index + 1] = {
            'name': member.tag.name,
            'eloRating': member.eloRating
        }
    return mem_dict
 
@register.simple_tag
def week_start():
    date = datetime.now() - timedelta(weeks=1)
    return date.strftime("%m/%d/%Y")
 
@register.simple_tag
def week_end():
    return datetime.now().strftime("%m/%d/%Y")
