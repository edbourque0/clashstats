import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from .models import Members, BattleLogs, Refresh
from django.shortcuts import render
from .clan import createclan
from .member import createmembers
from .battlelog import createbattlelog
from .searchlan import searchclanfnc
from .updateelo import updateelofcn
from .refreshclan import refreshclanfcn
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

load_dotenv()

url = 'https://api.clashroyale.com/v1/'
headers = {
            "Authorization": "Bearer " + os.getenv('CLASH_API_KEY'),
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
    members = list(Members.objects.all().order_by('-elo').exclude(elo=1000))

    # Global W/L
    for m in members:
        m.wins = BattleLogs.objects.filter(
            Q(winner1=m) | Q(winner2=m)
        ).count()
        m.losses = BattleLogs.objects.filter(
            Q(loser1=m) | Q(loser2=m)
        ).count()

    # === Weekly leaderboard ===
    now = timezone.now()
    # Monday = 0 ... Sunday = 6
    days_since_monday = now.weekday()
    last_monday = now - timedelta(days=days_since_monday)

    weekly_members = []
    for m in members:
        weekly_wins = BattleLogs.objects.filter(
            Q(winner1=m) | Q(winner2=m),
            battleTime__gte=last_monday,
        ).count()

        weekly_losses = BattleLogs.objects.filter(
            Q(loser1=m) | Q(loser2=m),
            battleTime__gte=last_monday,
        ).count()

        # Only show players who played this week
        if weekly_wins or weekly_losses:
            m.weekly_wins = weekly_wins
            m.weekly_losses = weekly_losses
            weekly_members.append(m)

    # Sort weekly leaderboard by weekly wins (then ELO as tiebreaker)
    weekly_members.sort(key=lambda x: (x.weekly_wins, x.elo), reverse=True)

    now = timezone.now()
    start_of_week = now - timedelta(days=now.weekday())

    if BattleLogs.objects.all().count() == 0:
      first_match = timezone.now()
    else:
        first_match = BattleLogs.objects.order_by('battleTime')[0].battleTime

    if Refresh.objects.all().count() == 0:
        last_refresh = timezone.now()
    else:
        last_refresh = Refresh.objects.order_by('-timestamp')[0].timestamp


    context = {
        "members": members,
        "weekly_members": weekly_members,
        "last_monday": last_monday,
        'first_match': first_match,
        'last_refresh': last_refresh,
        'battlecount': BattleLogs.objects.all().count(),
        'weeklybattlecount': BattleLogs.objects.filter(battleTime__gte=start_of_week,battleTime__lte=now,).count()
    }
    return render(request, "home.html", context)

@csrf_exempt
def searchClan(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        searchclanfnc(name, url, headers)

    else:
        return JsonResponse({'message':'Method not allowed'}, status=405)

@csrf_exempt
def addClan(request):
    if request.method == 'POST':
        clantag = request.POST.get('clantag')
        createclan(clantag, url, headers)
        return JsonResponse({'message': 'Clan added successfully'}, status=200)

    else:
        return JsonResponse({'message':'Method Not Allowed'}, status=405)

@csrf_exempt
def addMembers(request):
    if request.method == 'POST':
        clantag = request.POST.get('clantag')
        createmembers(clantag, url, headers)
        return JsonResponse({'message': 'Members added successfully'}, status=200)

    else:
        return JsonResponse({'message':'Method Not Allowed'}, status=405)



@csrf_exempt
def addBattleLog(request):
    if request.method == 'POST':
        playertag = request.POST.get('playertag')
        createbattlelog(playertag, url, headers)
        return JsonResponse({'message': 'Battles added successfully'}, status=200)

    else:
        return JsonResponse({'message':'Method Not Allowed'}, status=405)

@csrf_exempt
def refreshClan(request):
    if request.method == 'POST':
        clantag = request.POST.get('clantag')
        refreshclanfcn(clantag, url, headers)
        return JsonResponse({'message': 'Clan refreshed successfully'}, status=200)

    else:
        return JsonResponse({'message': 'Method Not Allowed'}, status=405)

@csrf_exempt
def updateelo(request):
    if request.method == 'GET':
        updateelofcn()
        return JsonResponse({'message': 'Elo updated successfully'}, status=200)

    else:
        return JsonResponse({'message': 'Method Not Allowed'}, status=405)