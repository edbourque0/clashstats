import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from .models import Members, BattleLogs, Refresh, WeeklyElo
from django.shortcuts import render
from .clan import createclan
from .member import createmembers
from .battlelog import createbattlelog
from .searchclan import searchclanfnc
from .updateelo import updateelofcn
from .refreshclan import refreshclanfcn
from .updateweeklyelo import updateweeklyelofcn
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta

load_dotenv()

url = "https://api.clashroyale.com/v1/"
headers = {
    "Authorization": "Bearer " + os.getenv("CLASH_API_KEY", ""),
}


def home(request):
    """
    Handles the processing of the homepage request. This function queries the
    `Members` model to retrieve a filtered and ordered list of members, excluding
    those with an ELO score of 1000, and sorts the remaining members by their ELO
    score in descending order. Ties in the ELO score are resolved by sorting
    alphabetically by the members' names. The retrieved member list is then passed
    to the "home.html" template for rendering.

    :param request: The HTTP request object containing metadata and other
        relevant information for processing the homepage view.
    :return: An HTTP response object with the rendered "home.html" template,
        including the filtered and ordered list of member data.
    """
    # Get all members with win/loss counts using annotations to avoid N+1 queries
    # Count battles where member appears as winner1, winner2, loser1, or loser2
    members = list(
        Members.objects.annotate(
            wins=Count('winner12member') + Count('winner22member'),
            losses=Count('loser12member') + Count('loser22member')
        ).exclude(elo=1000).order_by("-elo")
    )

    # === Weekly leaderboard ===
    now = timezone.now()
    dt = timezone.localtime(now)
    last_monday = (dt - timedelta(days=dt.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    # Get weekly members with prefetched related member data
    weekly_members = list(
        WeeklyElo.objects.filter(week=last_monday).select_related('member')
    )

    # Get battle logs for this week once and cache results
    weekly_battles = list(BattleLogs.objects.filter(battleTime__gte=last_monday).select_related(
        'winner1', 'winner2', 'loser1', 'loser2'
    ))

    # Get previous week's elo data for all members upfront
    member_tags = [m.member.tag for m in weekly_members]
    previous_elos = {}
    for elo_record in WeeklyElo.objects.filter(
        member__tag__in=member_tags
    ).exclude(week=last_monday).order_by('member', '-week'):
        # Only keep the most recent previous week for each member
        if elo_record.member.tag not in previous_elos:
            previous_elos[elo_record.member.tag] = elo_record.elo

    # Pre-compute wins and losses for all weekly members
    for m in weekly_members:
        player = m.member
        m.weekly_wins = sum(
            1 for b in weekly_battles
            if b.winner1 == player or b.winner2 == player
        )
        m.weekly_losses = sum(
            1 for b in weekly_battles
            if b.loser1 == player or b.loser2 == player
        )

        # Get previous week's elo for comparison
        prev_elo = previous_elos.get(player.tag)
        if prev_elo is not None:
            m.better_than_last_week = prev_elo < m.elo
        else:
            m.better_than_last_week = None

    # Get first match date and last refresh using first() instead of [0]
    first_battle = BattleLogs.objects.order_by("battleTime").first()
    first_match = first_battle.battleTime if first_battle else timezone.now()

    last_refresh_obj = Refresh.objects.order_by("-timestamp").first()
    last_refresh = last_refresh_obj.timestamp if last_refresh_obj else timezone.now()

    context = {
        "members": members,
        "weekly_members": weekly_members,
        "last_monday": last_monday,
        "first_match": first_match,
        "last_refresh": last_refresh,
        "battlecount": BattleLogs.objects.count(),
        "weeklybattlecount": len(weekly_battles),
    }
    return render(request, "home.html", context)


@csrf_exempt
def searchClan(request):
    if request.method == "POST":
        name = request.POST.get("name")
        searchclanfnc(name, url, headers)

    else:
        return JsonResponse({"message": "Method not allowed"}, status=405)


@csrf_exempt
def addClan(request):
    if request.method == "POST":
        clantag = request.POST.get("clantag")
        createclan(clantag, url, headers)
        return JsonResponse({"message": "Clan added successfully"}, status=200)

    else:
        return JsonResponse({"message": "Method Not Allowed"}, status=405)


@csrf_exempt
def addMembers(request):
    if request.method == "POST":
        clantag = request.POST.get("clantag")
        createmembers(clantag, url, headers)
        return JsonResponse({"message": "Members added successfully"}, status=200)

    else:
        return JsonResponse({"message": "Method Not Allowed"}, status=405)


@csrf_exempt
def addBattleLog(request):
    if request.method == "POST":
        playertag = request.POST.get("playertag")
        createbattlelog(playertag, url, headers)
        return JsonResponse({"message": "Battles added successfully"}, status=200)

    else:
        return JsonResponse({"message": "Method Not Allowed"}, status=405)


@csrf_exempt
def refreshClan(request):
    if request.method == "POST":
        clantag = request.POST.get("clantag")
        refreshclanfcn(clantag, url, headers)
        return JsonResponse({"message": "Clan refreshed successfully"}, status=200)

    else:
        return JsonResponse({"message": "Method Not Allowed"}, status=405)


@csrf_exempt
def updateelo(request):
    if request.method == "GET":
        updateelofcn()
        return JsonResponse({"message": "Elo updated successfully"}, status=200)

    else:
        return JsonResponse({"message": "Method Not Allowed"}, status=405)

@csrf_exempt
def updateweeklyelo(request):
    if request.method == "GET":
        updateweeklyelofcn()
        return JsonResponse({"message": "Weekly elo updated successfully"}, status=200)

    else:
        return JsonResponse({"message": "Method Not Allowed"}, status=405)