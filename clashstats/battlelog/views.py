from django.http import HttpResponse
from django.template import loader
import requests
from .models import Arena, GameMode, Clan, Card, Player, Battle

# Create your views here.
def home(request):
    template = loader.get_template('home.html')
    context = {}
    return HttpResponse(template.render(context, request))

def battlelog(request, tag):
    Arenas = Arena.objects.all().values()
    Gamemodes = GameMode.objects.all().values()
    Clans = Clan.objects.all().values()
    Cards = Card.objects.all().values()
    Players = Player.objects.all().values()
    Battles = Battle.objects.all().values()
    
    APIKEY = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImQ0YmNiMzEzLTRmZjYtNDJhZC05YTRkLWY5YjU1YmU5NzhlZCIsImlhdCI6MTcxMjI2OTg2OCwic3ViIjoiZGV2ZWxvcGVyLzNkNjhmM2MyLWM4ZmItNDAyYy0zZTU4LTk0YjIzMGY1Y2IzZCIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyI3NC4xMi4xNjkuMjMwIl0sInR5cGUiOiJjbGllbnQifV19.-bksJLAGJNvzXkxR5rrDkzUVgxMDYC7OQFFhKDOvimXboDA1ggddmbVod8qREXbq4yCYp8adTXOtNUy1YCFhMg'
    headers = {
        'Authorization': 'Bearer ' + APIKEY,
    }
    
    r = requests.get(f'https://api.clashroyale.com/v1/players/%23{tag}/battlelog', headers=headers)
    rawdata = r.json()
    
    for int, battle in enumerate(rawdata):
        data = rawdata[int]
        gamemode = GameMode.objects.get_or_create(
            id = data['gameMode']['id'],
            name = data['gameMode']['name']
        )
        
        arena = Arena.objects.get_or_create(
            id = data['arena']['id'],
            name = data['arena']['name']
        )
        
        for int, team in enumerate(data['team']):
            clanteam = Clan.objects.get_or_create(
                tag = data['team'][int]['clan']['tag'][1:],
                name = data['team'][int]['clan']['name'],
                badgeId = data['team'][int]['clan']['badgeId']
            )
            
            for card in data['team'][int]['cards']:
                card = Card.objects.get_or_create(
                    id = card['id'],
                    name = card['name'],
                    level = card['level'],
                    maxLevel = card['maxLevel'],
                    rarity = card['rarity'],
                    elixirCost = card['elixirCost'],
                    iconUrlsm = card['iconUrls']['medium']
                )
                
            supportCards = Card.objects.get_or_create(
                id = data['team'][int]['supportCards'][0]['id'],
                name = data['team'][int]['supportCards'][0]['name'],
                level = data['team'][int]['supportCards'][0]['level'],
                maxLevel = data['team'][int]['supportCards'][0]['maxLevel'],
                rarity = data['team'][int]['supportCards'][0]['rarity'],
                elixirCost = 0,
                iconUrlsm = data['team'][int]['supportCards'][0]['iconUrls']['medium']
            )
                
            team = Player.objects.get_or_create(
                tag = data['team'][int]['tag'][1:],
                name = data['team'][int]['name'],
                startingTrophies = data['team'][int]['startingTrophies'],
                crowns = data['team'][int]['crowns'],
                kingTowerHitPoints = data['team'][int]['kingTowerHitPoints'],
                princessTower1HitPoints = data['team'][int]['princessTowerHitPoints'][0] if data['team'][int].get('princessTowerHitPoints') and len(data['team'][int]['princessTowerHitPoints']) > 0 else 0,
                princessTower2HitPoints = data['team'][int]['princessTowerHitPoints'][1] if data['team'][int].get('princessTowerHitPoints') and len(data['team'][int]['princessTowerHitPoints']) > 1 else 0,
                clan = Clan.objects.get(tag=data['team'][int]['clan']['tag'][1:]),
                card1 = Card.objects.get(id=data['team'][int]['cards'][0]['id']),
                card2 = Card.objects.get(id=data['team'][int]['cards'][1]['id']),
                card3 = Card.objects.get(id=data['team'][int]['cards'][2]['id']),
                card4 = Card.objects.get(id=data['team'][int]['cards'][3]['id']),
                card5 = Card.objects.get(id=data['team'][int]['cards'][4]['id']),
                card6 = Card.objects.get(id=data['team'][int]['cards'][5]['id']),
                card7 = Card.objects.get(id=data['team'][int]['cards'][6]['id']),
                card8 = Card.objects.get(id=data['team'][int]['cards'][7]['id']),
                supportCards = Card.objects.get(id=data['team'][int]['supportCards'][0]['id']),
                globalRank = data['team'][int]['globalRank'],
                elixirLeaked = data['team'][int]['elixirLeaked']
            )
            
        for int, opponent in enumerate(data['opponent']):       
            clanopponent = Clan.objects.get_or_create(
                tag = data['opponent'][int]['clan']['tag'][1:],
                name = data['opponent'][int]['clan']['name'],
                badgeId = data['opponent'][int]['clan']['badgeId']
            )
        
            for card in data['opponent'][int]['cards']:
                card = Card.objects.get_or_create(
                    id = card['id'],
                    name = card['name'],
                    level = card['level'],
                    maxLevel = card['maxLevel'],
                    rarity = card['rarity'],
                    elixirCost = card['elixirCost'],
                    iconUrlsm = card['iconUrls']['medium']
                )
                
            supportCards = Card.objects.get_or_create(
                id = data['opponent'][int]['supportCards'][0]['id'],
                name = data['opponent'][int]['supportCards'][0]['name'],
                level = data['opponent'][int]['supportCards'][0]['level'],
                maxLevel = data['opponent'][int]['supportCards'][0]['maxLevel'],
                rarity = data['opponent'][int]['supportCards'][0]['rarity'],
                elixirCost = 0,
                iconUrlsm = data['opponent'][int]['supportCards'][0]['iconUrls']['medium']
            )
        
            opponent = Player.objects.get_or_create(
                tag = data['opponent'][int]['tag'][1:],
                name = data['opponent'][int]['name'],
                startingTrophies = data['opponent'][int]['startingTrophies'],
                crowns = data['opponent'][int]['crowns'],
                kingTowerHitPoints = data['opponent'][int]['kingTowerHitPoints'],
                princessTower1HitPoints=data['opponent'][int]['princessTowerHitPoints'][0] if data['team'][int].get('princessTowerHitPoints') and len(data['team'][int]['princessTowerHitPoints']) > 0 else 0,
                princessTower2HitPoints=data['opponent'][int]['princessTowerHitPoints'][1] if data['team'][int].get('princessTowerHitPoints') and len(data['team'][int]['princessTowerHitPoints']) > 1 else 0,
                clan = Clan.objects.get(tag=data['opponent'][int]['clan']['tag'][1:]),
                card1 = Card.objects.get(id=data['opponent'][int]['cards'][0]['id']),
                card2 = Card.objects.get(id=data['opponent'][int]['cards'][1]['id']),
                card3 = Card.objects.get(id=data['opponent'][int]['cards'][2]['id']),
                card4 = Card.objects.get(id=data['opponent'][int]['cards'][3]['id']),
                card5 = Card.objects.get(id=data['opponent'][int]['cards'][4]['id']),
                card6 = Card.objects.get(id=data['opponent'][int]['cards'][5]['id']),
                card7 = Card.objects.get(id=data['opponent'][int]['cards'][6]['id']),
                card8 = Card.objects.get(id=data['opponent'][int]['cards'][7]['id']),
                supportCards = Card.objects.get(id=data['opponent'][int]['supportCards'][0]['id']),
                globalRank = data['opponent'][int]['globalRank'],
                elixirLeaked = data['opponent'][int]['elixirLeaked']
            )
            
        battle = Battle.objects.create(
            battleTime = data['battleTime'],
            type = data['type'],
            isLadderTournament = data['isLadderTournament'],
            arena = Arena.objects.get(id=data['arena']['id']),
            gameMode = GameMode.objects.get(id=data['gameMode']['id']),
            deckSelection = data['deckSelection'],
            team = Player.objects.get(tag=data['team'][0]['tag'][1:]),
            opponent = Player.objects.get(tag=data['opponent'][0]['tag'][1:]),
            isHostedMatch = data['isHostedMatch'],
            leagueNumber = data['leagueNumber']   
        )
        
        template = loader.get_template('battlelog.html')
        context = {
            'arenas': Arenas,
            'gamemodes': Gamemodes,
            'clans': Clans,
            'cards': Cards,
            'players': Players,
            'battles': Battles,
        }
    
    return HttpResponse(template.render(context, request))
