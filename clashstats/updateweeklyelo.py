from datetime import timedelta
from django.utils import timezone
from .models import BattleLogs, WeeklyElo, Members
from django.db.models.functions import TruncWeek
import datetime
from collections import defaultdict

def get_week(dt):
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_default_timezone())

    dt = timezone.localtime(dt)
    monday = dt - timedelta(days=dt.weekday())

    monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    sunday = monday + timedelta(days=6)
    sunday = sunday.replace(hour=23, minute=59, second=59, microsecond=999999)

    return {
        'start': monday,
        'end': sunday,
    }

def update_weekly_elo():
    weeks = (
        BattleLogs.objects
        .annotate(week_start=TruncWeek('battleTime'))
        .values('week_start')
        .distinct()
        .order_by('week_start')
    )

    WeeklyElo.objects.all().delete()

    k = 32

    for week in weeks:
        week_start = week['week_start']
        week_end = week_start + datetime.timedelta(days=7)
        week_date = week_start.date()

        battles = (
            BattleLogs.objects
            .filter(battleTime__gte=week_start,
                    battleTime__lt=week_end)
            .order_by('battleTime')
        )

        current_elo = defaultdict(lambda: 1000.0)

        for battle in battles:
            w1 = battle.winner1
            w2 = battle.winner2
            l1 = battle.loser1
            l2 = battle.loser2

            if not (w1 and w2 and l1 and l2):
                continue

            w1_elo = current_elo[w1.tag]
            w2_elo = current_elo[w2.tag]
            l1_elo = current_elo[l1.tag]
            l2_elo = current_elo[l2.tag]

            winners_elo = (w1_elo + w2_elo) / 2
            losers_elo = (l1_elo + l2_elo) / 2

            winners_expected = 1 / (1 + 10 ** ((losers_elo - winners_elo) / 400))
            losers_expected  = 1 / (1 + 10 ** ((winners_elo - losers_elo) / 400))

            w1_elo_new = w1_elo + k * (1 - winners_expected)
            w2_elo_new = w2_elo + k * (1 - winners_expected)
            l1_elo_new = l1_elo + k * (0 - losers_expected)
            l2_elo_new = l2_elo + k * (0 - losers_expected)

            current_elo[w1.tag] = w1_elo_new
            current_elo[w2.tag] = w2_elo_new
            current_elo[l1.tag] = l1_elo_new
            current_elo[l2.tag] = l2_elo_new

        weekly_rows = []
        tag_to_member = {
            m.tag: m
            for m in Members.objects.filter(tag__in=current_elo.keys())
        }

        for member_tag, elo in current_elo.items():
            weekly_rows.append(
                WeeklyElo(
                    week=week_date,
                    member=tag_to_member[member_tag],
                                        elo=int(round(elo)),
                )
            )

        WeeklyElo.objects.bulk_create(weekly_rows)

    return