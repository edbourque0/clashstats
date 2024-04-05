import requests
from battlelog.models import Battle, Player, Card, Arena, Clan, GameMode


APIKEY = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImQ0YmNiMzEzLTRmZjYtNDJhZC05YTRkLWY5YjU1YmU5NzhlZCIsImlhdCI6MTcxMjI2OTg2OCwic3ViIjoiZGV2ZWxvcGVyLzNkNjhmM2MyLWM4ZmItNDAyYy0zZTU4LTk0YjIzMGY1Y2IzZCIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyI3NC4xMi4xNjkuMjMwIl0sInR5cGUiOiJjbGllbnQifV19.-bksJLAGJNvzXkxR5rrDkzUVgxMDYC7OQFFhKDOvimXboDA1ggddmbVod8qREXbq4yCYp8adTXOtNUy1YCFhMg'
headers = {
    'Authorization': 'Bearer ' + APIKEY,
}

def get_battlelog(tag):
    """Fetches the battlelog of a player with the given tag and adds the data to the database.

    Args:
        tag (str): player tag

    Returns:
        dict: json dictionary of the battlelog
    """
    r = requests.get(f'https://api.clashroyale.com/v1/players/%23{tag}/battlelog', headers=headers)
    data = r.json()[0]
    
    gamemode = GameMode.objects.create(
        id = data['gameMode']['id'],
        name = data['gameMode']['name']
    )
    
    arena = Arena.objects.create(
        id = data['arena']['id'],
        name = data['arena']['name']
    )
    
    clan = Clan.objects.create(
        tag = data['clan']['tag'],
        name = data['clan']['name'],
        badgeId = data['clan']['badgeId']
    )
    
    for card in data['team']['cards']:
        card = Card.objects.get_or_create(
            id = card['id'],
            name = card['name'],
            level = card['level'],
            maxLevel = card['maxLevel'],
            rarity = card['rarity'],
            elixirCost = card['elixirCost'],
            iconUrlsm = card['iconUrls']['medium'],
            iconUrlse = card['iconUrls']['evolutionMedium']
        )
        
    for card in data['opponent']['cards']:
        card = Card.objects.get_or_create(
            id = card['id'],
            name = card['name'],
            level = card['level'],
            maxLevel = card['maxLevel'],
            rarity = card['rarity'],
            elixirCost = card['elixirCost'],
            iconUrlsm = card['iconUrls']['medium'],
            iconUrlse = card['iconUrls']['evolutionMedium']
        )

    player = Player.objects.create(
        tag = data['player']['tag'],
        name = data['player']['name'],
        startingTrophies = data['player']['startingTrophies'],
        crowns = data['player']['crowns'],
        kingTowerHitPoints = data['player']['kingTowerHitPoints'],
        clan = data['player']['clan']['tag'],
        card1 = data['player']['cards'][0]['id'],
        card2 = data['player']['cards'][1]['id'],
        card3 = data['player']['cards'][2]['id'],
        card4 = data['player']['cards'][3]['id'],
        card5 = data['player']['cards'][4]['id'],
        card6 = data['player']['cards'][5]['id'],
        card7 = data['player']['cards'][6]['id'],
        card8 = data['player']['cards'][7]['id'],
        supportCards = data['player']['supportCards']['id'],
        globalRank = data['player']['globalRank'],
        elixirLeaked = data['player']['elixirLeaked']
    )
    
    battle = Battle.objects.create(
        battleTime = data['battleTime'],
        type = data['type'],
        isLadderTournament = data['isLadderTournament'],
        arena = data['arena']['id'],
        gamemode = data['gameMode']['id'],
        deckSelection = data['deckSelection'],
        team = data['team']['tag'],
        opponent = data['opponent']['tag'],
        isHostedMatch = data['isHostedMatch'],
        leagueNumber = data['leagueNumber']   
    )
    
    return r.json()

