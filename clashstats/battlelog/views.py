import requests
from clanranking.models import Members
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from .models import (
    Arena,
    GameMode,
    Clan,
    Card,
    Player,
    Battle,
    Badge,
    Achievement,
    FavoriteCard,
    PlayerInfo,
)
from dotenv import load_dotenv
load_dotenv()
import os


def home(request):
    template = loader.get_template("home.html")
    context = {
        "members": Members.objects.all(),
        "clans": Clan.objects.all(),
    }
    return HttpResponse(template.render(context, request))


def playerstatssearch(request):
    template = loader.get_template("playerstatssearch.html")
    context = {
        "members": Members.objects.all(),
    }
    return HttpResponse(template.render(context, request))


@csrf_exempt
def battlelog(request, tag):
    Arenas = Arena.objects.all().values()
    Gamemodes = GameMode.objects.all().values()
    Clans = Clan.objects.all().values()
    Cards = Card.objects.all().values()
    Players = Player.objects.select_related("card1").all()
    Battles = Battle.objects.select_related("opponent").all()
    PlayerInfos = PlayerInfo.objects.select_related("clan").all()
    Badges = Badge.objects.all()
    Achievements = Achievement.objects.all()
    FavoriteCards = FavoriteCard.objects.all()

    apikey = os.getenv("API_KEY")
    headers = {
        "Authorization": "Bearer " + apikey,
    }

    s = requests.get(
        f"https://api.clashroyale.com/v1/players/%23{tag}", headers=headers
    )
    r = requests.get(
        f"https://api.clashroyale.com/v1/players/%23{tag}/battlelog", headers=headers
    )

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
        GameMode.objects.get_or_create(
            id=data["gameMode"]["id"], name=data["gameMode"]["name"]
        )

        Arena.objects.get_or_create(
            id=data["arena"]["id"], name=data["arena"]["name"]
        )

        for ind, team in enumerate(data["team"]):
            if "clan" in data["team"][ind]:
                Clan.objects.get_or_create(
                    tag=data["team"][ind]["clan"]["tag"][1:],
                    name=data["team"][ind]["clan"]["name"],
                    badgeId=data["team"][ind]["clan"]["badgeId"],
                )

            for card in data["team"][ind]["cards"]:
                Card.objects.get_or_create(
                    id=f'{card["id"]}-{battint}{ind}',
                    name=card["name"],
                    level=card["level"],
                    maxLevel=card["maxLevel"],
                    rarity=card["rarity"],
                    elixirCost=0,
                    iconUrlsm=card["iconUrls"]["medium"],
                )

                if "elixirCost" in card:
                    Card.objects.filter(id=f'{card["id"]}-{battint}{ind}').update(
                        elixirCost=card["elixirCost"]
                    )

            Player.objects.get_or_create(
                tag=f'{data["team"][ind]["tag"][1:]}-{battint}',
                name=data["team"][ind]["name"],
                crowns=data["team"][ind]["crowns"],
                kingTowerHitPoints=data["team"][ind]["kingTowerHitPoints"],
                princessTower1HitPoints=(
                    data["team"][ind]["princessTowersHitPoints"][0]
                    if data["team"][ind].get("princessTowersHitPoints")
                       and len(data["team"][ind]["princessTowersHitPoints"]) > 0
                    else 0
                ),
                princessTower2HitPoints=(
                    data["team"][ind]["princessTowersHitPoints"][1]
                    if data["team"][ind].get("princessTowersHitPoints")
                       and len(data["team"][ind]["princessTowersHitPoints"]) > 1
                    else 0
                ),
                clan=Clan.objects.get(
                    tag=(
                        data["team"][ind]["clan"]["tag"][1:]
                        if "clan" in data["team"][ind]
                        else "None"
                    )
                ),
                card1=Card.objects.get(
                    id=f'{data["team"][ind]["cards"][0]["id"]}-{battint}{ind}'
                ),
                card2=Card.objects.get(
                    id=f'{data["team"][ind]["cards"][1]["id"]}-{battint}{ind}'
                ),
                card3=Card.objects.get(
                    id=f'{data["team"][ind]["cards"][2]["id"]}-{battint}{ind}'
                ),
                card4=Card.objects.get(
                    id=f'{data["team"][ind]["cards"][3]["id"]}-{battint}{ind}'
                ),
                card5=Card.objects.get(
                    id=f'{data["team"][ind]["cards"][4]["id"]}-{battint}{ind}'
                ),
                card6=Card.objects.get(
                    id=f'{data["team"][ind]["cards"][5]["id"]}-{battint}{ind}'
                ),
                card7=Card.objects.get(
                    id=f'{data["team"][ind]["cards"][6]["id"]}-{battint}{ind}'
                ),
                card8=Card.objects.get(
                    id=f'{data["team"][ind]["cards"][7]["id"]}-{battint}{ind}'
                ),
                elixirLeaked=data["team"][ind]["elixirLeaked"],
            )

            if len(data["team"][ind]["supportCards"]) == 1:
                Card.objects.get_or_create(
                    id=f"{data['team'][ind]['supportCards'][0]['id']}-{battint}{ind}",
                    name=data["team"][ind]["supportCards"][0]["name"],
                    level=data["team"][ind]["supportCards"][0]["level"],
                    maxLevel=data["team"][ind]["supportCards"][0]["maxLevel"],
                    rarity=data["team"][ind]["supportCards"][0]["rarity"],
                    elixirCost=0,
                    iconUrlsm=data["team"][ind]["supportCards"][0]["iconUrls"][
                        "medium"
                    ],
                )

                Player.objects.filter(
                    tag=f"{data['team'][ind]['tag'][1:]}-{battint}"
                ).update(
                    supportCards=Card.objects.get(
                        id=f"{data['team'][ind]['supportCards'][0]['id']}-{battint}{ind}"
                    )
                )

            if "clan" in data["team"][ind]:
                Player.objects.filter(
                    tag=f"{data['team'][ind]['tag'][1:]}-{battint}{ind}"
                ).update(
                    clan=Clan.objects.get(tag=data["team"][ind]["clan"]["tag"][1:]),
                )
            else:
                Player.objects.filter(
                    tag=f"{data['team'][ind]['tag'][1:]}-{battint}{ind}"
                ).update(
                    clan=Clan.objects.get(tag="None"),
                )

        for ind, opponent in enumerate(data["opponent"]):
            if "clan" in data["opponent"][ind]:
                Clan.objects.get_or_create(
                    tag=data["opponent"][ind]["clan"]["tag"][1:],
                    name=data["opponent"][ind]["clan"]["name"],
                    badgeId=data["opponent"][ind]["clan"]["badgeId"],
                )
            else:
                Clan.objects.get_or_create(
                    tag="None", name="None", badgeId="00000000"
                )

            for card in data["opponent"][ind]["cards"]:
                Card.objects.get_or_create(
                    id=f'{card["id"]}-{battint}{ind + 10000}',
                    name=card["name"],
                    level=card["level"],
                    maxLevel=card["maxLevel"],
                    rarity=card["rarity"],
                    elixirCost=0,
                    iconUrlsm=card["iconUrls"]["medium"],
                )

                if "elixirCost" in card:
                    Card.objects.filter(id=f'{card["id"]}-{battint}{ind + 10000}').update(
                        elixirCost=card["elixirCost"]
                    )

            Player.objects.get_or_create(
                tag=f"{data['opponent'][ind]['tag'][1:]}-{battint}",
                name=data["opponent"][ind]["name"],
                crowns=data["opponent"][ind]["crowns"],
                kingTowerHitPoints=data["opponent"][ind]["kingTowerHitPoints"],
                princessTower1HitPoints=(
                    data["opponent"][ind]["princessTowerHitPoints"][0]
                    if data["team"][ind].get("princessTowerHitPoints") and len(
                        data["team"][ind]["princessTowerHitPoints"]) > 0
                    else 0
                ),
                princessTower2HitPoints=(
                    data["opponent"][ind]["princessTowerHitPoints"][1]
                    if data["team"][ind].get("princessTowerHitPoints") and len(
                        data["team"][ind]["princessTowerHitPoints"]) > 1
                    else 0
                ),
                card1=Card.objects.get(
                    id=f"{data['opponent'][ind]['cards'][0]['id']}-{battint}{ind + 10000}"
                ),
                card2=Card.objects.get(
                    id=f"{data['opponent'][ind]['cards'][1]['id']}-{battint}{ind + 10000}"
                ),
                card3=Card.objects.get(
                    id=f"{data['opponent'][ind]['cards'][2]['id']}-{battint}{ind + 10000}"
                ),
                card4=Card.objects.get(
                    id=f"{data['opponent'][ind]['cards'][3]['id']}-{battint}{ind + 10000}"
                ),
                card5=Card.objects.get(
                    id=f"{data['opponent'][ind]['cards'][4]['id']}-{battint}{ind + 10000}"
                ),
                card6=Card.objects.get(
                    id=f"{data['opponent'][ind]['cards'][5]['id']}-{battint}{ind + 10000}"
                ),
                card7=Card.objects.get(
                    id=f"{data['opponent'][ind]['cards'][6]['id']}-{battint}{ind + 10000}"
                ),
                card8=Card.objects.get(
                    id=f"{data['opponent'][ind]['cards'][7]['id']}-{battint}{ind + 10000}"
                ),
                elixirLeaked=data["opponent"][ind]["elixirLeaked"],
            )

            if len(data["opponent"][ind]["supportCards"]) == 1:
                Card.objects.get_or_create(
                    id=f"{data['opponent'][ind]['supportCards'][0]['id']}-{battint}{ind + 10000}",
                    name=data["opponent"][ind]["supportCards"][0]["name"],
                    level=data["opponent"][ind]["supportCards"][0]["level"],
                    maxLevel=data["opponent"][ind]["supportCards"][0]["maxLevel"],
                    rarity=data["opponent"][ind]["supportCards"][0]["rarity"],
                    elixirCost=0,
                    iconUrlsm=data["opponent"][ind]["supportCards"][0]["iconUrls"][
                        "medium"
                    ],
                )

                Player.objects.filter(
                    tag=f"{data['opponent'][ind]['tag'][1:]}-{battint}"
                ).update(
                    supportCards=Card.objects.get(
                        id=f"{data['opponent'][ind]['supportCards'][0]['id']}-{battint}{ind + 10000}"
                    )
                )

            if "clan" in data["opponent"][ind]:
                Player.objects.filter(
                    tag=f"{data['opponent'][ind]['tag'][1:]}-{battint}"
                ).update(
                    clan=Clan.objects.get(tag=data["opponent"][ind]["clan"]["tag"][1:]),
                )
            else:
                Player.objects.filter(
                    tag=f"{data['opponent'][ind]['tag'][1:]}-{battint}"
                ).update(
                    clan=Clan.objects.get(tag="None"),
                )

        Battle.objects.create(
            battleTime=data["battleTime"],
            type=data["type"],
            isLadderTournament=data["isLadderTournament"],
            arena=Arena.objects.get(id=data["arena"]["id"]),
            gameMode=GameMode.objects.get(id=data["gameMode"]["id"]),
            deckSelection=data["deckSelection"],
            team=Player.objects.get(tag=f"{data['team'][ind]['tag'][1:]}-{battint}"),
            opponent=Player.objects.get(
                tag=f"{data['opponent'][ind]['tag'][1:]}-{battint}"
            ),
            isHostedMatch=data["isHostedMatch"],
            leagueNumber=data["leagueNumber"],
        )

    PlayerInfo.objects.create(
        tag=rawdatas["tag"],
        name=rawdatas["name"],
        expLevel=rawdatas["expLevel"],
        trophies=rawdatas["trophies"],
        bestTrophies=rawdatas["bestTrophies"],
        wins=rawdatas["wins"],
        losses=rawdatas["losses"],
        battleCount=rawdatas["battleCount"],
        threeCrownWins=rawdatas["threeCrownWins"],
        challengeCardsWon=rawdatas["challengeCardsWon"],
        challengeMaxWins=rawdatas["challengeMaxWins"],
        tournamentCardsWon=rawdatas["tournamentCardsWon"],
        tournamentBattleCount=rawdatas["tournamentBattleCount"],
        role=rawdatas["role"],
        donations=rawdatas["donations"],
        donationsReceived=rawdatas["donationsReceived"],
        totalDonations=rawdatas["totalDonations"],
        warDayWins=rawdatas["warDayWins"],
        clanCardsCollected=rawdatas["clanCardsCollected"],
        clan=Clan.objects.get(tag=rawdatas["clan"]["tag"][1:]),
        arena=Arena.objects.get(id=rawdatas["arena"]["id"]),
        starPoints=rawdatas["starPoints"],
        legacyTrophyRoadHighScore=rawdatas["legacyTrophyRoadHighScore"],
        currentPathOfLegendSeasonResult=rawdatas["currentPathOfLegendSeasonResult"],
        lastPathOfLegendSeasonResult=rawdatas["lastPathOfLegendSeasonResult"],
        bestPathOfLegendSeasonResult=rawdatas["bestPathOfLegendSeasonResult"],
        totalExpPoints=rawdatas["totalExpPoints"],
    )

    for badge in rawdatas["badges"]:
        Badge.objects.create(
            name=badge["name"],
            progress=badge["progress"],
            level=badge["level"],
            maxLevel=badge["maxLevel"],
            target=badge["target"] if "target" in badge else 0,
            iconUrls=badge["iconUrls"]["large"],
        )

    for achievement in rawdatas["achievements"]:
        Achievement.objects.create(
            name=achievement["name"],
            stars=achievement["stars"],
            value=achievement["value"],
            target=achievement["target"],
            info=achievement["info"],
            completionInfo=achievement["completionInfo"],
        )

    FavoriteCard.objects.create(
        name=rawdatas["currentFavouriteCard"]["name"],
        id=rawdatas["currentFavouriteCard"]["id"],
        maxLevel=rawdatas["currentFavouriteCard"]["maxLevel"],
        elixirCost=rawdatas["currentFavouriteCard"]["elixirCost"],
        iconUrls=rawdatas["currentFavouriteCard"]["iconUrls"]["medium"],
        rarity=rawdatas["currentFavouriteCard"]["rarity"],
    )

    template = loader.get_template("battlelog.html")
    context = {
        "arenas": Arenas,
        "gamemodes": Gamemodes,
        "clans": Clans,
        "cards": Cards,
        "players": Players,
        "battles": Battles,
        "playerinfo": PlayerInfos,
        "achievements": Achievements,
        "favoritecard": FavoriteCards,
        "badge": Badges,
    }

    return HttpResponse(template.render(context, request))
