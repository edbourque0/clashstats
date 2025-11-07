import os
from contextlib import nullcontext
from django.db.models.functions import NullIf
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import loader
import requests
import json
from dotenv import load_dotenv
from .models import Clans, Members

load_dotenv()

url = 'https://api.clashroyale.com/v1/'
headers = {
            "Authorization": "Bearer " + os.getenv('CLASH_API_KEY'),
        }

def home(request):
    template = loader.get_template("home.html")
    context = {}
    return HttpResponse(template.render(context, request))

@csrf_exempt
def searchClan(request):
    if request.method == 'POST':
        if request.POST.get('name') != '':
            name = request.POST.get('name')
            r = requests.get(url=f'{url}clans', headers=headers, params={'name': name})
            return JsonResponse(r.json(), status=200)

        else:
            return JsonResponse({'message': 'name parameter missing'}, status=400)

    else:
        return JsonResponse({'message':'Method not allowed'}, status=405)

@csrf_exempt
def refresh(request):
    if request.method == 'POST':
        clantag = request.POST.get('clantag')

        r = requests.get(url=f'{url}clans/%23{clantag[1:]}', headers=headers, params={'name':clantag})
        clan = r.json()

        Clans.objects.create(
            tag=clan['tag'],
            name=clan['name'],
            type=clan['type'],
            badgeId=clan['badgeId'],
            location=clan['location']['countryCode'],
            donationsPerWeek=clan['donationsPerWeek'],
            members=clan['members']
        )

        return JsonResponse({'message': 'Clan added successfully'}, status=200)

    else:
        return JsonResponse({'message':'Method Not Allowed'}, status=405)

@csrf_exempt
def addMembers(request):
    if request.method == 'POST':
        clantag = request.POST.get('clantag')

        r = requests.get(url=f'{url}clans/%23{clantag[1:]}/members', headers=headers)

        members = r.json()['items']
        for member in members:
            Members.objects.update_or_create(
                tag = member['tag'],
                clanTag = Clans.objects.get(tag=clantag),
                name = member['name'],
                role = member['role'],
                lastSeen = member['lastSeen'],
                expLevel = member['expLevel'],
                trophies = member['trophies'],
                clanRank = member['clanRank'],
                donations = member['donations'],
                donationsReceived = member['donationsReceived']
            )

        return JsonResponse({'message': 'Members added successfully'}, status=200)

    else:
        return JsonResponse({'message':'Method Not Allowed'}, status=405)

# @csrf_exempt
# def addBattleLog(request):
#     if request.method == 'POST':
#         playertag = request.POST.get('playertag')
#
#         r = requests.get(url=f'{url}players/%23{playertag[1:]}/battlelog', headers=headers)
#         battles = r.json()
#
#         for battle in battles:
#
#
#         return JsonResponse({'message': 'Members added successfully'}, status=200)
#
#     else:
#         return JsonResponse({'message':'Method Not Allowed'}, status=405)