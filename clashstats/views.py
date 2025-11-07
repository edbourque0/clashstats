import os
from contextlib import nullcontext
from django.db.models.functions import NullIf
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import loader
import requests
import json
from dotenv import load_dotenv
from .models import Clans, Members, BattleLogs
import hashlib

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
def addClan(request):
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



@csrf_exempt
def addBattleLog(request):
    """This view creates the battles for a specific member"""

    if request.method == 'POST':
        playertag = request.POST.get('playertag')

        r = requests.get(url=f'{url}players/%23{playertag[1:]}/battlelog', headers=headers)
        battles = r.json()

        def defineWinnersLosers(battle):
            """
            This function determines the winners and losers of a battle
            Args:
                battle (dict): json of the battle returned by the Clash Royale API
            """
            team1crowns = battle['team'][0]['crowns']
            team2crowns = battle['opponent'][0]['crowns']

            if team1crowns > team2crowns:
                winnersandlosers = {
                    'winner1': battle['team'][0]['tag'],
                    'winner2': battle['team'][1]['tag'],
                    'loser1': battle['opponent'][0]['tag'],
                    'loser2': battle['opponent'][1]['tag'],
                    'time' : battle['battleTime']
                }

                h = hashlib.sha256(json.dumps(winnersandlosers, separators=(",", ":"), sort_keys=True).encode("utf-8")).hexdigest()
                winnersandlosers['hash'] = h

                return winnersandlosers

            else:
                winnersandlosers = {
                    'winner1': battle['opponent'][0]['tag'],
                    'winner2': battle['opponent'][1]['tag'],
                    'loser1': battle['team'][0]['tag'],
                    'loser2': battle['team'][1]['tag'],
                    'time': battle['battleTime']
                }

                h = hashlib.sha256(json.dumps(winnersandlosers, separators=(",", ":"), sort_keys=True).encode("utf-8")).hexdigest()
                winnersandlosers['hash'] = h

                return winnersandlosers

        for battle in battles:
            if len(battle['team']) == 2:
                
                if battle['type'] == 'clanMate2v2':
                    winlose = defineWinnersLosers(battle)

                    # Check if battle log doesn't already exist
                    if not BattleLogs.objects.filter(id=winlose['hash']).exists():
                        BattleLogs.objects.create(
                            id=winlose['hash'],
                            type=battle['type'],
                            battleTime=battle['battleTime'],
                            gameMode=battle['gameMode']['name'],
                            winner1=Members.objects.get(tag=winlose['winner1']),
                            winner2=Members.objects.get(tag=winlose['winner2']),
                            loser1=Members.objects.get(tag=winlose['loser1']),
                            loser2=Members.objects.get(tag=winlose['loser2']),
                        )

        return JsonResponse({'message': 'Battles added successfully'}, status=200)

    else:
        return JsonResponse({'message':'Method Not Allowed'}, status=405)