from django.http import HttpResponse
from django.template import loader
import requests
from .models import Arena, GameMode, Clan, Card, Player, Battle, Badge, Achievement, FavoriteCard, PlayerInfo

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
    Players = Player.objects.select_related('card1').all()
    Battles = Battle.objects.select_related('opponent').all()
    PlayerInfos = PlayerInfo.objects.select_related('clan').all()
    Badges = Badge.objects.all()
    Achievements = Achievement.objects.all()
    FavoriteCards = FavoriteCard.objects.all()
    
    APIKEY = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImQ0YmNiMzEzLTRmZjYtNDJhZC05YTRkLWY5YjU1YmU5NzhlZCIsImlhdCI6MTcxMjI2OTg2OCwic3ViIjoiZGV2ZWxvcGVyLzNkNjhmM2MyLWM4ZmItNDAyYy0zZTU4LTk0YjIzMGY1Y2IzZCIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyI3NC4xMi4xNjkuMjMwIl0sInR5cGUiOiJjbGllbnQifV19.-bksJLAGJNvzXkxR5rrDkzUVgxMDYC7OQFFhKDOvimXboDA1ggddmbVod8qREXbq4yCYp8adTXOtNUy1YCFhMg'
    headers = {
        'Authorization': 'Bearer ' + APIKEY,
    }
    
    s = requests.get(f'https://api.clashroyale.com/v1/players/%23{tag}', headers=headers)
    r = requests.get(f'https://api.clashroyale.com/v1/players/%23{tag}/battlelog', headers=headers)
    
    rawdata = r.json()
    rawdatas = s.json()
    
    Battle.objects.all().delete()
    Player.objects.all().delete()
    Card.objects.all().delete()
    Clan.objects.all().delete()
    GameMode.objects.all().delete()
    Arena.objects.all().delete()
    PlayerInfo.objects.all().delete()
    Badge.objects.all().delete()
    Achievement.objects.all().delete()
    FavoriteCard.objects.all().delete()
    
    for battint, battle in enumerate(rawdata):
        data = rawdata[battint]
        gamemode = GameMode.objects.get_or_create(
            id = data['gameMode']['id'],
            name = data['gameMode']['name']
        )
        
        arena = Arena.objects.get_or_create(
            id = data['arena']['id'],
            name = data['arena']['name']
        )
        
        for int, team in enumerate(data['team']):
            if 'clan' in data['team'][int]:
                clanteam = Clan.objects.get_or_create(
                    tag = data['team'][int]['clan']['tag'][1:],
                    name = data['team'][int]['clan']['name'],
                    badgeId = data['team'][int]['clan']['badgeId']
                )
            
            for card in data['team'][int]['cards']:
                card1 = Card.objects.get_or_create(
                    id = f'{card["id"]}-{battint}{int}',
                    name = card['name'],
                    level = card['level'],
                    maxLevel = card['maxLevel'],
                    rarity = card['rarity'],
                    elixirCost = 0,
                    iconUrlsm = card['iconUrls']['medium']
                )
                
                if 'elixirCost' in card:
                    Card.objects.filter(id=f'{card["id"]}-{battint}{int}').update(
                        elixirCost = card['elixirCost']
                    )
                
                
            team = Player.objects.get_or_create(
                tag = f'{data["team"][int]["tag"][1:]}-{battint}',
                name = data['team'][int]['name'],
                crowns = data['team'][int]['crowns'],
                kingTowerHitPoints = data['team'][int]['kingTowerHitPoints'],
                princessTower1HitPoints = data['team'][int]['princessTowersHitPoints'][0] if data['team'][int].get('princessTowersHitPoints') and len(data['team'][int]['princessTowersHitPoints']) > 0 else 0,
                princessTower2HitPoints = data['team'][int]['princessTowersHitPoints'][1] if data['team'][int].get('princessTowersHitPoints') and len(data['team'][int]['princessTowersHitPoints']) > 1 else 0,
                clan = Clan.objects.get(tag=data['team'][int]['clan']['tag'][1:] if 'clan' in data['team'][int] else 'None'),
                card1 = Card.objects.get(id=f'{data["team"][int]["cards"][0]["id"]}-{battint}{int}'),
                card2 = Card.objects.get(id=f'{data["team"][int]["cards"][1]["id"]}-{battint}{int}'),
                card3 = Card.objects.get(id=f'{data["team"][int]["cards"][2]["id"]}-{battint}{int}'),
                card4 = Card.objects.get(id=f'{data["team"][int]["cards"][3]["id"]}-{battint}{int}'),
                card5 = Card.objects.get(id=f'{data["team"][int]["cards"][4]["id"]}-{battint}{int}'),
                card6 = Card.objects.get(id=f'{data["team"][int]["cards"][5]["id"]}-{battint}{int}'),
                card7 = Card.objects.get(id=f'{data["team"][int]["cards"][6]["id"]}-{battint}{int}'),
                card8 = Card.objects.get(id=f'{data["team"][int]["cards"][7]["id"]}-{battint}{int}'),
                elixirLeaked = data['team'][int]['elixirLeaked']
            )
            
            if len(data['team'][int]['supportCards']) == 1:
                supportCards = Card.objects.get_or_create(
                    id = f"{data['team'][int]['supportCards'][0]['id']}-{battint}{int}",
                    name = data['team'][int]['supportCards'][0]['name'],
                    level = data['team'][int]['supportCards'][0]['level'],
                    maxLevel = data['team'][int]['supportCards'][0]['maxLevel'],
                    rarity = data['team'][int]['supportCards'][0]['rarity'],
                    elixirCost = 0,
                    iconUrlsm = data['team'][int]['supportCards'][0]['iconUrls']['medium']
                )
                
                Player.objects.filter(tag=f"{data['team'][int]['tag'][1:]}-{battint}").update(supportCards = Card.objects.get(id=f"{data['team'][int]['supportCards'][0]['id']}-{battint}{int}"))
                
            
            if 'clan' in data['team'][int]:
                clanopponent = Player.objects.filter(tag=f"{data['team'][int]['tag'][1:]}-{battint}{int}").update(
                    clan = Clan.objects.get(tag=data['team'][int]['clan']['tag'][1:]),
                )
            else:
                clanopponent = Player.objects.filter(tag=f"{data['team'][int]['tag'][1:]}-{battint}{int}").update(
                    clan = Clan.objects.get(tag='None'),
                )
            
        for int, opponent in enumerate(data['opponent']):       
            if 'clan' in data['opponent'][int]:
                clanopponent = Clan.objects.get_or_create(
                    tag = data['opponent'][int]['clan']['tag'][1:],
                    name = data['opponent'][int]['clan']['name'],
                    badgeId = data['opponent'][int]['clan']['badgeId']
                )
            else:
                clanopponent = Clan.objects.get_or_create(
                    tag = 'None',
                    name = 'None',
                    badgeId = '00000000'
                )
        
            for card in data['opponent'][int]['cards']:
                card1 = Card.objects.get_or_create(
                    id = f'{card["id"]}-{battint}{int+10000}',
                    name = card['name'],
                    level = card['level'],
                    maxLevel = card['maxLevel'],
                    rarity = card['rarity'],
                    elixirCost = 0,
                    iconUrlsm = card['iconUrls']['medium']
                )
                
                if 'elixirCost' in card:
                    Card.objects.filter(id=f'{card["id"]}-{battint}{int+10000}').update(
                        elixirCost = card['elixirCost']
                    )
                
        
            opponent = Player.objects.get_or_create(
                tag = f"{data['opponent'][int]['tag'][1:]}-{battint}",
                name = data['opponent'][int]['name'],
                crowns = data['opponent'][int]['crowns'],
                kingTowerHitPoints = data['opponent'][int]['kingTowerHitPoints'],
                princessTower1HitPoints=data['opponent'][int]['princessTowerHitPoints'][0] if data['team'][int].get('princessTowerHitPoints') and len(data['team'][int]['princessTowerHitPoints']) > 0 else 0,
                princessTower2HitPoints=data['opponent'][int]['princessTowerHitPoints'][1] if data['team'][int].get('princessTowerHitPoints') and len(data['team'][int]['princessTowerHitPoints']) > 1 else 0,
                card1 = Card.objects.get(id=f"{data['opponent'][int]['cards'][0]['id']}-{battint}{int+10000}"),
                card2 = Card.objects.get(id=f"{data['opponent'][int]['cards'][1]['id']}-{battint}{int+10000}"),
                card3 = Card.objects.get(id=f"{data['opponent'][int]['cards'][2]['id']}-{battint}{int+10000}"),
                card4 = Card.objects.get(id=f"{data['opponent'][int]['cards'][3]['id']}-{battint}{int+10000}"),
                card5 = Card.objects.get(id=f"{data['opponent'][int]['cards'][4]['id']}-{battint}{int+10000}"),
                card6 = Card.objects.get(id=f"{data['opponent'][int]['cards'][5]['id']}-{battint}{int+10000}"),
                card7 = Card.objects.get(id=f"{data['opponent'][int]['cards'][6]['id']}-{battint}{int+10000}"),
                card8 = Card.objects.get(id=f"{data['opponent'][int]['cards'][7]['id']}-{battint}{int+10000}"),
                elixirLeaked = data['opponent'][int]['elixirLeaked']
            )
            
            if len(data['opponent'][int]['supportCards']) == 1:
                supportCards = Card.objects.get_or_create(
                    id = f"{data['opponent'][int]['supportCards'][0]['id']}-{battint}{int+10000}",
                    name = data['opponent'][int]['supportCards'][0]['name'],
                    level = data['opponent'][int]['supportCards'][0]['level'],
                    maxLevel = data['opponent'][int]['supportCards'][0]['maxLevel'],
                    rarity = data['opponent'][int]['supportCards'][0]['rarity'],
                    elixirCost = 0,
                    iconUrlsm = data['opponent'][int]['supportCards'][0]['iconUrls']['medium']
                )
                
                
                Player.objects.filter(tag=f"{data['opponent'][int]['tag'][1:]}-{battint}").update(supportCards = Card.objects.get(id=f"{data['opponent'][int]['supportCards'][0]['id']}-{battint}{int+10000}"))
            
            if 'clan' in data['opponent'][int]:
                clanopponent = Player.objects.filter(tag=f"{data['opponent'][int]['tag'][1:]}-{battint}").update(
                    clan = Clan.objects.get(tag=data['opponent'][int]['clan']['tag'][1:]),
                )
            else:
                clanopponent = Player.objects.filter(tag=f"{data['opponent'][int]['tag'][1:]}-{battint}").update(
                    clan = Clan.objects.get(tag='None'),
                )
            
        battle = Battle.objects.create(
            battleTime = data['battleTime'],
            type = data['type'],
            isLadderTournament = data['isLadderTournament'],
            arena = Arena.objects.get(id=data['arena']['id']),
            gameMode = GameMode.objects.get(id=data['gameMode']['id']),
            deckSelection = data['deckSelection'],
            team = Player.objects.get(tag=f"{data['team'][int]['tag'][1:]}-{battint}"),
            opponent = Player.objects.get(tag=f"{data['opponent'][int]['tag'][1:]}-{battint}"),
            isHostedMatch = data['isHostedMatch'],
            leagueNumber = data['leagueNumber']   
        )
    
    PlayerInfo.objects.create(
        tag = rawdatas['tag'],
        name = rawdatas['name'],
        expLevel = rawdatas['expLevel'],
        trophies = rawdatas['trophies'],
        bestTrophies = rawdatas['bestTrophies'],
        wins = rawdatas['wins'],
        losses = rawdatas['losses'],
        battleCount = rawdatas['battleCount'],
        threeCrownWins = rawdatas['threeCrownWins'],
        challengeCardsWon = rawdatas['challengeCardsWon'],
        challengeMaxWins = rawdatas['challengeMaxWins'],
        tournamentCardsWon = rawdatas['tournamentCardsWon'],
        tournamentBattleCount = rawdatas['tournamentBattleCount'],
        role = rawdatas['role'],
        donations = rawdatas['donations'],
        donationsReceived = rawdatas['donationsReceived'],
        totalDonations = rawdatas['totalDonations'],
        warDayWins = rawdatas['warDayWins'],
        clanCardsCollected = rawdatas['clanCardsCollected'],
        clan = Clan.objects.get(tag=rawdatas['clan']['tag'][1:]),
        arena = Arena.objects.get(id=rawdatas['arena']['id']),
        starPoints = rawdatas['starPoints'],
        legacyTrophyRoadHighScore = rawdatas['legacyTrophyRoadHighScore'],
        currentPathOfLegendSeasonResult = rawdatas['currentPathOfLegendSeasonResult'],
        lastPathOfLegendSeasonResult = rawdatas['lastPathOfLegendSeasonResult'],
        bestPathOfLegendSeasonResult = rawdatas['bestPathOfLegendSeasonResult'],
        totalExpPoints = rawdatas['totalExpPoints']
    )
    
    for badge in rawdatas['badges']:
        Badge.objects.create(
            name = badge['name'],
            progress = badge['progress'],
            level = badge['level'],
            maxLevel = badge['maxLevel'],
            target = badge['target'] if 'target' in badge else 0,
            iconUrls = badge['iconUrls']['large'],
        )
    
    for achievement in rawdatas['achievements']:
        Achievement.objects.create(
            name = achievement['name'],
            stars = achievement['stars'],
            value = achievement['value'],
            target = achievement['target'],
            info = achievement['info'],
            completionInfo = achievement['completionInfo'],
        )
    
    FavoriteCard.objects.create(
        name = rawdatas['currentFavouriteCard']['name'],
        id = rawdatas['currentFavouriteCard']['id'],
        maxLevel = rawdatas['currentFavouriteCard']['maxLevel'],
        elixirCost = rawdatas['currentFavouriteCard']['elixirCost'],
        iconUrls = rawdatas['currentFavouriteCard']['iconUrls']['medium'],
        rarity = rawdatas['currentFavouriteCard']['rarity']
    )
    
    template = loader.get_template('battlelog.html')
    context = {
        'arenas': Arenas,
        'gamemodes': Gamemodes,
        'clans': Clans,
        'cards': Cards,
        'players': Players,
        'battles': Battles,
        'playerinfo': PlayerInfos,
        'achievements': Achievements,
        'favoritecard': FavoriteCards,
        'badge': Badges
    }
    
    return HttpResponse(template.render(context, request))
