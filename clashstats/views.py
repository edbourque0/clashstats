import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from .models import Members
from django.shortcuts import render
from .clan import createclan
from .member import createmembers
from .battlelog import createbattlelog
from .searchlan import searchclanfnc
from .updateelo import updateelofcn
from .refreshclan import refreshclanfcn

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