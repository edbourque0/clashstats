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
from django.shortcuts import render

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
    members = (
        Members.objects.only("name", "elo").exclude(elo=1000)
        .order_by("-elo", "name")  # highest ELO first, tie-break by name
    )
    return render(request, "home.html", {"members": members})

@csrf_exempt
def searchClan(request):
    """
    Executes a clan search based on the provided name parameter in the POST request.
    It forwards the request to an external API and retrieves the corresponding result.

    :param request: The HTTP request object containing details about the client's request.
    :type request: HttpRequest
    :return: A JSON response with the search results if the request is valid, an error
        message with HTTP 400 if the 'name' parameter is missing, or 405 if the
        request method is not POST.
    :rtype: JsonResponse
    """
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
    """
    Handles the addition of a clan to the database. It retrieves clan data
    from an external API using the provided clan tag, then updates or creates
    the clan entry in the database based on the data fetched. Only HTTP POST
    requests are allowed for this operation. In case of unsupported HTTP methods,
    a proper response is returned.

    :param request: Django HttpRequest object
    :return: JsonResponse with a success message and status 200 for valid POST
             requests, or a JsonResponse with an error message and status 405
             for unsupported methods
    """
    if request.method == 'POST':
        clantag = request.POST.get('clantag')

        r = requests.get(url=f'{url}clans/%23{clantag[1:]}', headers=headers, params={'name':clantag})
        clan = r.json()

        Clans.objects.update_or_create(
            tag=clan['tag'],
            defaults={
                'name': clan['name'],
                'type': clan['type'],
                'badgeId': clan['badgeId'],
                'location': clan['location']['countryCode'],
                'donationsPerWeek': clan['donationsPerWeek'],
                'members': clan['members']
            }
        )

        return JsonResponse({'message': 'Clan added successfully'}, status=200)

    else:
        return JsonResponse({'message':'Method Not Allowed'}, status=405)

@csrf_exempt
def addMembers(request):
    """
    Adds and updates clan members in the database based on a POST request.

    This function fetches the list of members of a specified clan from an external
    API using the supplied clan tag. It updates the database with the current state
    of the members or creates new entries if required. If the request method is
    not POST, it returns an appropriate response indicating that the method is not
    allowed.

    :param request: Django's HTTP request object containing request data and context.
    :type request: HttpRequest
    :return: JSON response containing a message indicating the result of the operation.
    :rtype: JsonResponse
    """
    if request.method == 'POST':
        clantag = request.POST.get('clantag')

        r = requests.get(url=f'{url}clans/%23{clantag[1:]}/members', headers=headers)

        members = r.json()['items']
        for member in members:
            Members.objects.update_or_create(
                tag = member['tag'],
                defaults={
                    'clanTag': Clans.objects.get(tag=clantag),
                    'name': member['name'],
                    'role': member['role'],
                    'lastSeen': member['lastSeen'],
                    'expLevel': member['expLevel'],
                    'trophies': member['trophies'],
                    'clanRank': member['clanRank'],
                    'donations': member['donations'],
                    'donationsReceived': member['donationsReceived']
                }
            )

        return JsonResponse({'message': 'Members added successfully'}, status=200)

    else:
        return JsonResponse({'message':'Method Not Allowed'}, status=405)



@csrf_exempt
def addBattleLog(request):
    """
    Handles a request to add battle logs to the database. This function fetches battle details
    from the Clash Royale API based on a player's tag provided in a HTTP POST request. It
    extracts and processes relevant battles to identify winners and losers for each eligible
    battle log. Validated and structured battle logs are stored in the database if unique.

    Note:
        Only POST requests are allowed. The function interacts with external APIs and the
        database.

    :param request: HTTP request object that contains the player's tag (`playertag`) as a
        parameter in a POST request.
    :type request: HttpRequest

    :return: A JSON response with a success message if battles are added successfully or an
        error message for unsupported HTTP methods.
    :rtype: JsonResponse
    """

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

@csrf_exempt
def refreshClan(request):
    """
    Handles the refreshing of clan data, clan member details, and their battlelogs
    by making API requests. This function is primarily triggered by a POST request
    and processes the clan information using the provided clantag.

    :param request: Django HTTP request object
    :type request: HttpRequest
    :return: JSON response indicating success or failure of the operation
    :rtype: JsonResponse
    """
    if request.method == 'POST':
        """ Refresh clan """
        clantag = request.POST.get('clantag')
        response = requests.post('http://localhost:8000/api/v1/clan', data={'clantag': clantag})

        """ Refresh clan members """
        response = requests.post('http://localhost:8000/api/v1/members', data={'clantag': clantag})

        """ Refresh battlelog """
        for member in Members.objects.select_related('clanTag').all():
            response = requests.post('http://localhost:8000/api/v1/battlelog', data={'playertag': member.tag})

        return JsonResponse({'message': 'Clan refreshed successfully'}, status=200)

    else:
        return JsonResponse({'message': 'Method Not Allowed'}, status=405)

@csrf_exempt
def updateelo(request):
    """
    Updates ELO rankings for all battles that have not yet had their ELOs calculated.

    This function retrieves all BattleLogs, sorts them by battle time, and iterates
    through each battle that has not been marked as ELO-calculated. For each battle,
    it computes and updates the ELO ratings of the winners and losers based on the
    ELO calculation formula. Once the ratings are updated, the battle is flagged as
    ELO-calculated. The updates are applied to the Members database. If the request
    method is not GET, a response indicating the method is not allowed is returned.

    :param request: HTTP request object containing details of the incoming request.
    :type request: HttpRequest
    :return: JsonResponse indicating the success or failure of the operation.
    :rtype: JsonResponse
    """
    if request.method == 'GET':
        sortedbattles = BattleLogs.objects.all().order_by('battleTime')

        for battle in sortedbattles:
            if not battle.elocalculated:
                """ Define common variables """
                winnerselo = (battle.winner1.elo + battle.winner2.elo) / 2
                loserselo = (battle.loser1.elo + battle.loser2.elo) / 2
                winnersexpectedscore = 1 / (1 + 10 ** ((loserselo - winnerselo)/400))
                losersexpectedscore = 1 / (1 + 10 ** ((winnerselo - loserselo) / 400))

                """ Compute and update ELO of winners """
                w1newelo = battle.winner1.elo + 32 * (1 - winnersexpectedscore)
                w2newelo = battle.winner2.elo + 32 * (1 - winnersexpectedscore)
                Members.objects.filter(tag=battle.winner1.tag).update(elo=w1newelo)
                Members.objects.filter(tag=battle.winner2.tag).update(elo=w2newelo)

                """ Compute and update ELO of losers """
                l1newelo = battle.loser1.elo + 32 * (0 - losersexpectedscore)
                l2newelo = battle.loser2.elo + 32 * (0 - losersexpectedscore)
                Members.objects.filter(tag=battle.loser1.tag).update(elo=l1newelo)
                Members.objects.filter(tag=battle.loser2.tag).update(elo=l2newelo)

                """ Mark battle as elo-calculated """
                BattleLogs.objects.filter(id=battle.id).update(elocalculated=True)

        return JsonResponse({'message': 'Elo updated successfully'}, status=200)
    else:
        return JsonResponse({'message': 'Method Not Allowed'}, status=405)