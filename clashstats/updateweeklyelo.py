# python
from collections import defaultdict
from datetime import timedelta
from functools import lru_cache
from django.utils import timezone
from .models import BattleLogs, WeeklyElo

INITIAL_ELO = 1000
K_FACTOR = 32

def get_week_start(dt):
    """
    Returns Monday 00:00 (ISO week start) for a datetime, keeping tz.
    """
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_default_timezone())

    dt = timezone.localtime(dt)
    monday = dt - timedelta(days=dt.weekday())
    return monday.replace(hour=0, minute=0, second=0, microsecond=0)


def update_elo(rating_a, rating_b, result_a, k=K_FACTOR):
    """
    Simple Elo update for one game.
    result_a: 1 = A wins, 0.5 = draw, 0 = A loses
    Returns (new_rating_a, new_rating_b).
    """
    expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    expected_b = 1 - expected_a

    new_a = rating_a + k * (result_a - expected_a)
    new_b = rating_b + k * ((1 - result_a) - expected_b)

    return new_a, new_b


@lru_cache(maxsize=None)
def _starting_rating(member_id, week_start):
    previous = (
        WeeklyElo.objects.filter(member_id=member_id, week__lt=week_start)
        .order_by("-week")
        .values_list("elo", flat=True)
        .first()
    )
    return previous if previous is not None else INITIAL_ELO


def updateweeklyelofcn():
    now = timezone.now()
    current_week_start = get_week_start(now)
    battles_by_week = defaultdict(list)

    for battle in BattleLogs.objects.all().order_by("battleTime"):
        week_start = get_week_start(battle.battleTime)
        battles_by_week[week_start].append(battle)

    for week_start in sorted(battles_by_week.keys()):
        is_locked_week = week_start < current_week_start

        if is_locked_week and WeeklyElo.objects.filter(week=week_start).exists():
            continue

        if week_start == current_week_start:
            WeeklyElo.objects.filter(week=week_start).delete()

        ratings = {}

        def ensure_rating(member):
            member_id = member.pk
            if member_id not in ratings:
                ratings[member_id] = _starting_rating(member_id, week_start)
            return ratings[member_id]

        for battle in battles_by_week[week_start]:
            winners = [battle.winner1, battle.winner2]
            losers = [battle.loser1, battle.loser2]

            winner_ratings = [ensure_rating(player) for player in winners]
            loser_ratings = [ensure_rating(player) for player in losers]

            win_team_rating = sum(winner_ratings) / len(winner_ratings)
            lose_team_rating = sum(loser_ratings) / len(loser_ratings)

            new_win_team, new_lose_team = update_elo(win_team_rating, lose_team_rating, 1)

            win_delta = new_win_team - win_team_rating
            lose_delta = new_lose_team - lose_team_rating

            for player in winners:
                ratings[player.pk] = ensure_rating(player) + win_delta
            for player in losers:
                ratings[player.pk] = ensure_rating(player) + lose_delta

        bulk_objs = [
            WeeklyElo(member_id=member_id, week=week_start, elo=int(round(elo)))
            for member_id, elo in ratings.items()
        ]

        WeeklyElo.objects.bulk_create(bulk_objs, ignore_conflicts=True)