import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from .models import Members, BattleLogs, Refresh, WeeklyElo
from django.shortcuts import render
from .clan import create_clan
from .member import create_members
from .battlelog import create_battlelog
from .searchclan import search_clan
from .updateelo import update_elo
from .refreshclan import refresh_clan
from .updateweeklyelo import update_weekly_elo
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict

load_dotenv()

url = "https://api.clashroyale.com/v1/"
headers = {
    "Authorization": "Bearer " + os.getenv("CLASH_API_KEY", ""),
}


def home(request):
    # --- All-time leaderboard ---
    # Use annotate() to count wins and losses in a single SQL query instead of
    # issuing 2 queries per member in a Python loop (N+1 problem).
    members = (
        Members.objects
        .exclude(elo=1000)
        .annotate(
            wins=Count("winner12member", distinct=True) + Count("winner22member", distinct=True),
            losses=Count("loser12member", distinct=True) + Count("loser22member", distinct=True),
        )
        .order_by("-elo")
    )

    # --- Week boundary (computed once, reused everywhere) ---
    now = timezone.now()
    dt = timezone.localtime(now)
    last_monday = (dt - timedelta(days=dt.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    # --- Weekly leaderboard ---
    weekly_members = list(
        WeeklyElo.objects
        .filter(week=last_monday)
        .select_related("member")
    )

    if weekly_members:
        # Fetch ALL this week's battles in one query instead of 2 queries per player
        weekly_battles = list(
            BattleLogs.objects
            .filter(battleTime__gte=last_monday)
            .values("winner1_id", "winner2_id", "loser1_id", "loser2_id")
        )

        weekly_wins = defaultdict(int)
        weekly_losses = defaultdict(int)
        for b in weekly_battles:
            weekly_wins[b["winner1_id"]] += 1
            weekly_wins[b["winner2_id"]] += 1
            weekly_losses[b["loser1_id"]] += 1
            weekly_losses[b["loser2_id"]] += 1

        # Fetch previous week's ELOs in one query instead of 1 query per player.
        # Also fixes the sort-order bug: the original code used order_by("week")[1]
        # (ascending), which returned the second-oldest week rather than last week.
        prev_week = last_monday - timedelta(weeks=1)
        prev_elo_map = dict(
            WeeklyElo.objects
            .filter(week=prev_week)
            .values_list("member_id", "elo")
        )

        for m in weekly_members:
            tag = m.member_id
            m.weekly_wins   = weekly_wins.get(tag, 0)
            m.weekly_losses = weekly_losses.get(tag, 0)
            prev_elo = prev_elo_map.get(tag)
            if prev_elo is not None:
                m.better_than_last_week = prev_elo < m.elo

    # --- Metadata ---
    # Use .exists() instead of .count() == 0 for the presence check, and compute
    # the battle count once rather than calling .count() three separate times.
    if not BattleLogs.objects.exists():
        first_match = now
        battlecount = 0
    else:
        first_match = BattleLogs.objects.order_by("battleTime").values_list("battleTime", flat=True).first()
        battlecount = BattleLogs.objects.count()

    last_refresh = (
        Refresh.objects.order_by("-timestamp").values_list("timestamp", flat=True).first()
        or now
    )

    weeklybattlecount = BattleLogs.objects.filter(
        battleTime__gte=last_monday,
        battleTime__lte=now,
    ).count()

    context = {
        "members": members,
        "weekly_members": weekly_members,
        "last_monday": last_monday,
        "first_match": first_match,
        "last_refresh": last_refresh,
        "battlecount": battlecount,
        "weeklybattlecount": weeklybattlecount,
    }
    return render(request, "home.html", context)


@csrf_exempt
def searchClan(request):
    if request.method == "POST":
        name = request.POST.get("name")
        return search_clan(name, url, headers)
    else:
        return JsonResponse({"message": "Method not allowed"}, status=405)


@csrf_exempt
def addClan(request):
    if request.method == "POST":
        clantag = request.POST.get("clantag")
        create_clan(clantag, url, headers)
        return JsonResponse({"message": "Clan added successfully"}, status=200)

    else:
        return JsonResponse({"message": "Method Not Allowed"}, status=405)


@csrf_exempt
def addMembers(request):
    if request.method == "POST":
        clantag = request.POST.get("clantag")
        create_members(clantag, url, headers)
        return JsonResponse({"message": "Members added successfully"}, status=200)

    else:
        return JsonResponse({"message": "Method Not Allowed"}, status=405)


@csrf_exempt
def addBattleLog(request):
    if request.method == "POST":
        playertag = request.POST.get("playertag")
        create_battlelog(playertag, url, headers)
        return JsonResponse({"message": "Battles added successfully"}, status=200)

    else:
        return JsonResponse({"message": "Method Not Allowed"}, status=405)


@csrf_exempt
def refreshClan(request):
    if request.method == "POST":
        clantag = request.POST.get("clantag")
        refresh_clan(clantag, url, headers)
        return JsonResponse({"message": "Clan refreshed successfully"}, status=200)

    else:
        return JsonResponse({"message": "Method Not Allowed"}, status=405)


@csrf_exempt
def updateelo(request):
    if request.method == "GET":
        update_elo()
        return JsonResponse({"message": "Elo updated successfully"}, status=200)

    else:
        return JsonResponse({"message": "Method Not Allowed"}, status=405)

@csrf_exempt
def updateweeklyelo(request):
    if request.method == "GET":
        update_weekly_elo()
        return JsonResponse({"message": "Weekly elo updated successfully"}, status=200)

    else:
        return JsonResponse({"message": "Method Not Allowed"}, status=405)
