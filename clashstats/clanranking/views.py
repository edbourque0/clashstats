from django.http import HttpResponse
from django.template import loader
import requests
from .models import Members, Clans, Battles

def clanranking(request, clantag):
    #Request variables
    APIKEY = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImQ0YmNiMzEzLTRmZjYtNDJhZC05YTRkLWY5YjU1YmU5NzhlZCIsImlhdCI6MTcxMjI2OTg2OCwic3ViIjoiZGV2ZWxvcGVyLzNkNjhmM2MyLWM4ZmItNDAyYy0zZTU4LTk0YjIzMGY1Y2IzZCIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyI3NC4xMi4xNjkuMjMwIl0sInR5cGUiOiJjbGllbnQifV19.-bksJLAGJNvzXkxR5rrDkzUVgxMDYC7OQFFhKDOvimXboDA1ggddmbVod8qREXbq4yCYp8adTXOtNUy1YCFhMg'
    headers = {
        'Authorization': 'Bearer ' + APIKEY,
    }
    c = requests.get(f'https://api.clashroyale.com/v1/clans/%23{clantag}', headers=headers)
    
    rawclan = c.json()
    #-----------------
    
    for memint, member in enumerate(rawclan['memberList']):
        if Members.objects.filter(tag=member['tag'][1:]).exists() == False:
            Members.objects.update_or_create(
                tag = member['tag'][1:],
                name = member['name'],
                role = member['role'],
                lastSeen = member['lastSeen'],
                expLevel = member['expLevel'],
                trophies = member['trophies'],
                arena = member['arena']['name'],
                clanRank = member['clanRank'],
                clanChestPoints = member['clanChestPoints'],
                clanPoints = 0,
                wonBattles = 0,
                lostBattles = 0
            )
            
    if Clans.objects.filter(tag=rawclan['tag']).exists() == False:
        Clans.objects.update_or_create(
            tag = rawclan['tag'],
            name = rawclan['name'],
            type = rawclan['type'],
            description = rawclan['description'],
            badgeId = rawclan['badgeId'],
            clanScore = rawclan['clanScore'],
            clanWarTrophies = rawclan['clanWarTrophies'],
            requiredTrophies = rawclan['requiredTrophies'],
            donationsPerWeek = rawclan['donationsPerWeek']
        )
    
    for member in Members.objects.all():
        b = requests.get(f'https://api.clashroyale.com/v1/players/%23{member.tag}/battlelog', headers=headers)
        rawb = b.json()
        for battint, battle in enumerate(rawb):
            if Members.objects.filter(tag=rawb[battint]['team'][0]['tag'][1:]).exists() and Members.objects.filter(tag=rawb[battint]['opponent'][0]['tag'][1:]).exists() and Clans.objects.filter(tag=rawb[battint]['team'][0]['clan']['tag']).exists() and Clans.objects.filter(tag=rawb[battint]['opponent'][0]['clan']['tag']).exists() and Battles.objects.filter(id = f'{rawb[battint]["battleTime"]}-{rawb[battint]["opponent"][0]["tag"][1:]}-{rawb[battint]["team"][0]["tag"][1:]}').exists() == False:
                rawbattles = rawb[battint]
                Battles.objects.update_or_create(
                    id = f'{rawbattles['battleTime']}-{rawbattles['team'][0]['tag'][1:]}-{rawbattles['opponent'][0]['tag'][1:]}',
                    battleTime = rawbattles['battleTime'],
                    type = rawbattles['type'],
                    isLadderTournament = rawbattles['isLadderTournament'],
                    arena = rawbattles['arena']['name'],
                    gameMode = rawbattles['gameMode']['name'],
                    deckSelection = rawbattles['deckSelection'],
                    team1Tag = Members.objects.get(tag=rawbattles['team'][0]['tag'][1:]),
                    team1Clan = Clans.objects.get(tag=rawbattles['team'][0]['clan']['tag']),
                    team1Crowns = rawbattles['team'][0]['crowns'],
                    team2Tag = Members.objects.get(tag=rawbattles['team'][1]['tag'][1:]) if len(rawbattles['team']) > 1 else None,
                    team2Clan = Clans.objects.get(tag=rawbattles['team'][1]['clan']['tag']) if len(rawbattles['team']) > 1 else None,
                    team2Crowns = rawbattles['team'][1]['crowns'] if len(rawbattles['team']) > 1 else None,
                    opponent1Tag = Members.objects.get(tag=rawbattles['opponent'][0]['tag'][1:]),
                    opponent1Clan = Clans.objects.get(tag=rawbattles['opponent'][0]['clan']['tag']),
                    opponent1Crowns = rawbattles['opponent'][0]['crowns'],
                    opponent2Tag = Members.objects.get(tag=rawbattles['opponent'][1]['tag'][1:]) if len(rawbattles['opponent']) > 1 else None,
                    opponent2Clan = Clans.objects.get(tag=rawbattles['opponent'][1]['clan']['tag']) if len(rawbattles['opponent']) > 1 else None,
                    opponent2Crowns = rawbattles['opponent'][1]['crowns'] if len(rawbattles['opponent']) > 1 else None,
                    isHostedMatch = rawbattles['isHostedMatch']
                )

    for currentBattle in Battles.objects.all():
        if currentBattle.team1Clan == currentBattle.opponent1Clan:
            
            winnerPts = max(currentBattle.team1Crowns, currentBattle.opponent1Crowns)
            loserPts = min(currentBattle.team1Crowns, currentBattle.opponent1Crowns)
            winnerTag = str(currentBattle.team1Tag) if winnerPts == currentBattle.team1Crowns else str(currentBattle.opponent1Tag)
            loserTag = str(currentBattle.team1Tag) if loserPts == currentBattle.team1Crowns else str(currentBattle.opponent1Tag)
            
            Battles.objects.filter(id = currentBattle.id).update(
                winner1Tag = Members.objects.get(tag = winnerTag),
                loser1Tag = Members.objects.get(tag = loserTag)
            )
            
            Members.objects.filter(tag = winnerTag ).update(
                clanPoints = Members.objects.get(tag = winnerTag).clanPoints + winnerPts
            )
            
            Members.objects.filter(tag = loserTag ).update(
                clanPoints = Members.objects.get(tag = loserTag).clanPoints + loserPts
            )
            
    for member in Members.objects.all():
        Members.objects.filter(tag=member.tag).update(
            wonBattles=Battles.objects.filter(winner1Tag=member.tag).count(),
            lostBattles=Battles.objects.filter(loser1Tag=member.tag).count()
        )
            
    template = loader.get_template('clanranking.html')
    context = {
        'clans': Clans.objects.all(),
        'members': Members.objects.all(),
        'battles': Battles.objects.all()
    }
    return HttpResponse(template.render(context, request))
