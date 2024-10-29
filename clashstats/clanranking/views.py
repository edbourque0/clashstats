from django.http import HttpResponse
from django.template import loader
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.db.models import Q
from django.utils import timezone
import requests
from .models import Members, Clans, Battles
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()
import os


def clanrankingsearch(request):
    template = loader.get_template("clanrankinghome.html")
    context = {
        "clans": Clans.objects.all(),
    }
    return HttpResponse(template.render(context, request))


@csrf_exempt
def clanrefresh(request, clantag):
    # Request variables
    apikey = os.environ.get("API_KEY")
    headers = {
        "Authorization": "Bearer " + apikey,
    }
    c = requests.get(
        f"https://api.clashroyale.com/v1/clans/%23{clantag}", headers=headers
    )

    rawclan = c.json()
    for memint, member in enumerate(rawclan["memberList"]):
        if not Members.objects.filter(tag=member["tag"][1:]).exists():
            Members.objects.update_or_create(
                tag=member["tag"][1:],
                name=member["name"],
                role=member["role"],
                lastSeen=member["lastSeen"],
                expLevel=member["expLevel"],
                trophies=member["trophies"],
                arena=member["arena"]["name"],
                clanRank=member["clanRank"],
                clanChestPoints=member["clanChestPoints"],
                clanPoints=0,
                wonBattles=0,
                lostBattles=0,
            )

    if not Clans.objects.filter(tag=rawclan["tag"]).exists():
        Clans.objects.update_or_create(
            tag=rawclan["tag"],
            name=rawclan["name"],
            type=rawclan["type"],
            description=rawclan["description"],
            badgeId=rawclan["badgeId"],
            clanScore=rawclan["clanScore"],
            clanWarTrophies=rawclan["clanWarTrophies"],
            requiredTrophies=rawclan["requiredTrophies"],
            donationsPerWeek=rawclan["donationsPerWeek"],
        )

    else:
        Clans.objects.filter(tag=rawclan["tag"]).update(lastUpdated=timezone.now())

    for member in Members.objects.all():
        b = requests.get(
            f"https://api.clashroyale.com/v1/players/%23{member.tag}/battlelog",
            headers=headers,
        )
        rawb = b.json()
        for battint, battle in enumerate(rawb):
            if (
                Members.objects.filter(tag=rawb[battint]["team"][0]["tag"][1:]).exists()
                and Members.objects.filter(
                    tag=rawb[battint]["opponent"][0]["tag"][1:]
                ).exists()
                and Clans.objects.filter(
                    tag=rawb[battint]["team"][0]["clan"]["tag"]
                ).exists()
                and Clans.objects.filter(
                    tag=rawb[battint]["opponent"][0]["clan"]["tag"]
                ).exists()
                and Battles.objects.filter(
                    id=f'{rawb[battint]["battleTime"]}-{rawb[battint]["opponent"][0]["tag"][1:]}-{rawb[battint]["team"][0]["tag"][1:]}'
                ).exists()
                == False
            ):
                rawbattles = rawb[battint]
                Battles.objects.update_or_create(
                    id=f"{rawbattles['battleTime']}-{rawbattles['team'][0]['tag'][1:]}-{rawbattles['opponent'][0]['tag'][1:]}",
                    battleTime=rawbattles["battleTime"],
                    type=rawbattles["type"],
                    isLadderTournament=rawbattles["isLadderTournament"],
                    arena=rawbattles["arena"]["name"],
                    gameMode=rawbattles["gameMode"]["name"],
                    deckSelection=rawbattles["deckSelection"],
                    team1Tag=Members.objects.get(tag=rawbattles["team"][0]["tag"][1:]),
                    team1Clan=Clans.objects.get(
                        tag=rawbattles["team"][0]["clan"]["tag"]
                    ),
                    team1Crowns=rawbattles["team"][0]["crowns"],
                    team2Tag=(
                        Members.objects.get(tag=rawbattles["team"][1]["tag"][1:])
                        if len(rawbattles["team"]) > 1
                        else None
                    ),
                    team2Clan=(
                        Clans.objects.get(tag=rawbattles["team"][1]["clan"]["tag"])
                        if len(rawbattles["team"]) > 1
                        else None
                    ),
                    team2Crowns=(
                        rawbattles["team"][1]["crowns"]
                        if len(rawbattles["team"]) > 1
                        else None
                    ),
                    opponent1Tag=Members.objects.get(
                        tag=rawbattles["opponent"][0]["tag"][1:]
                    ),
                    opponent1Clan=Clans.objects.get(
                        tag=rawbattles["opponent"][0]["clan"]["tag"]
                    ),
                    opponent1Crowns=rawbattles["opponent"][0]["crowns"],
                    opponent2Tag=(
                        Members.objects.get(tag=rawbattles["opponent"][1]["tag"][1:])
                        if len(rawbattles["opponent"]) > 1
                        else None
                    ),
                    opponent2Clan=(
                        Clans.objects.get(tag=rawbattles["opponent"][1]["clan"]["tag"])
                        if len(rawbattles["opponent"]) > 1
                        else None
                    ),
                    opponent2Crowns=(
                        rawbattles["opponent"][1]["crowns"]
                        if len(rawbattles["opponent"]) > 1
                        else None
                    ),
                    isHostedMatch=rawbattles["isHostedMatch"],
                )

    for currentBattle in Battles.objects.all():
        if currentBattle.team1Clan == currentBattle.opponent1Clan:

            winnerPts = max(currentBattle.team1Crowns, currentBattle.opponent1Crowns)
            loserPts = min(currentBattle.team1Crowns, currentBattle.opponent1Crowns)
            winnerTag = (
                str(currentBattle.team1Tag)
                if winnerPts == currentBattle.team1Crowns
                else str(currentBattle.opponent1Tag)
            )
            loserTag = (
                str(currentBattle.team1Tag)
                if loserPts == currentBattle.team1Crowns
                else str(currentBattle.opponent1Tag)
            )

            Battles.objects.filter(id=currentBattle.id).update(
                winner1Tag=Members.objects.get(tag=winnerTag),
                loser1Tag=Members.objects.get(tag=loserTag),
            )

            Members.objects.filter(tag=winnerTag).update(
                clanPoints=Members.objects.get(tag=winnerTag).clanPoints + winnerPts
            )

            Members.objects.filter(tag=loserTag).update(
                clanPoints=Battles.objects.filter(
                    team1Tag=Members.objects.get(tag=loserTag)
                ).count()
            )

    for member in Members.objects.all():
        Members.objects.filter(tag=member.tag).update(
            wonBattles=Battles.objects.filter(winner1Tag=member.tag).count(),
            lostBattles=Battles.objects.filter(loser1Tag=member.tag).count(),
        )

    for member in Members.objects.all():
        Members.objects.filter(tag=member.tag).update(eloRating=1000)

    for battle in Battles.objects.all():
        expectation_t = 1 / (
            1
            + 10 ** ((battle.opponent1Tag.eloRating - battle.team1Tag.eloRating) / 400)
        )
        expectation_o = 1 - expectation_t
        sAt = 1 if battle.team1Tag == battle.winner1Tag else 0
        sAo = 1 if battle.opponent1Tag == battle.winner1Tag else 0
        newRanking_t = battle.team1Tag.eloRating + 32 * (sAt - expectation_t)
        newRanking_o = battle.opponent1Tag.eloRating + 32 * (sAo - expectation_o)
        Members.objects.filter(tag=battle.team1Tag).update(eloRating=newRanking_t)
        Members.objects.filter(tag=battle.opponent1Tag).update(eloRating=newRanking_o)

    return redirect(f'/clanranking/{clantag}')


@csrf_exempt
def clanranking(request, clantag):
    template = loader.get_template("clanranking.html")
    tu = Clans.objects.get(tag=f"#{clantag}").lastUpdated
    tn = timezone.now()
    context = {
        "clan": Clans.objects.get(tag=f"#{clantag}"),
        "currentclantag": Clans.objects.get(tag=f"#{clantag}").tag,
        "members": Members.objects.filter(~Q(eloRating=1000))
        .order_by("-eloRating")
        .all(),
        "battles": Battles.objects.all(),
        "lastUpdatedMin": round((tn - tu).total_seconds() / 60),
        "today": datetime.strftime(datetime.now(), "%Y-%m-%d"),
    }

    default_start_date = datetime.now() - timedelta(days=7)
    default_end_date = datetime.now()

    if request.method == 'POST':
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else default_start_date
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59) if end_date_str else default_end_date

        contextDates = {
            "start_date": start_date,
            "end_date": end_date,
        }

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render_to_string('ranking_table.html', contextDates, request)
            return HttpResponse(html)
    return HttpResponse(template.render(context, request))

def twovtwo(request):
    players = {'UCPRP8P0C': 'Will', 'PQGY0QUG': 'Alex', 'J0CQYLC8J': 'Godet', 'CJG89UPQR': 'Ed', 'Q8YL0V0YG': 'Gui'}

    def playerToList(name):
        if name == 'Will':
            return Will
        if name == 'Ed':
            return Ed
        if name == 'Godet':
            return Godet
        if name == 'Alex':
            return Alex
        if name == 'Gui':
            return Gui

    def getPlayerName(tag):
        return players[tag]
    
    Gui = {'Will': 0, 'Ed': 0, 'Godet': 0, 'Alex': 0}
    Ed = {'Will': 0, 'Gui': 0, 'Godet': 0, 'Alex': 0}
    Will = {'Ed': 0, 'Gui': 0, 'Godet': 0, 'Alex': 0}
    Godet = {'Will': 0, 'Ed': 0, 'Gui': 0, 'Alex': 0}
    Alex = {'Will': 0, 'Ed': 0, 'Godet': 0, 'Gui': 0}

    def generate2v2Ranking1():
        for battle in Battles.objects.all():
            for player in players:
                if battle.winner1Tag_id == player and battle.gameMode[0:10] == 'TeamVsTeam' and battle.gameMode[-8:] == 'Friendly':
                    if battle.winner1Tag_id == battle.opponent1Tag_id:
                        if battle.opponent2Tag_id in players.keys():
                            playerToList(players[player])[getPlayerName(battle.opponent2Tag_id)] = playerToList(players[player]).get(getPlayerName(battle.opponent2Tag_id)) + 1
                            playerToList(getPlayerName(battle.opponent2Tag_id))[getPlayerName(battle.winner1Tag_id)] = playerToList(getPlayerName(battle.opponent2Tag_id)).get(getPlayerName(battle.winner1Tag_id)) + 1
                    if battle.winner1Tag_id == battle.opponent2Tag_id:
                        if battle.opponent1Tag_id in players.keys():
                            playerToList(players[player])[getPlayerName(battle.opponent1Tag_id)] = playerToList(players[player]).get(getPlayerName(battle.opponent1Tag_id)) + 1
                            playerToList(getPlayerName(battle.opponent1Tag_id))[getPlayerName(battle.winner1Tag_id)] = playerToList(getPlayerName(battle.opponent1Tag_id)).get(getPlayerName(battle.winner1Tag_id)) + 1
                    if battle.winner1Tag_id == battle.team1Tag_id:
                        if battle.team2Tag_id in players.keys():
                            playerToList(players[player])[getPlayerName(battle.team2Tag_id)] = playerToList(players[player]).get(getPlayerName(battle.opponent1Tag_id)) + 1
                            playerToList(getPlayerName(battle.team2Tag_id))[getPlayerName(battle.winner1Tag_id)] = playerToList(getPlayerName(battle.team2Tag_id)).get(getPlayerName(battle.winner1Tag_id)) + 1
                    if battle.winner1Tag_id == battle.team2Tag_id:
                        if battle.team1Tag_id in players.keys():
                            playerToList(players[player])[getPlayerName(battle.team1Tag_id)] = playerToList(players[player]).get(getPlayerName(battle.opponent2Tag_id)) + 1
                            playerToList(getPlayerName(battle.team1Tag_id))[getPlayerName(battle.winner1Tag_id)] = playerToList(getPlayerName(battle.team1Tag_id)).get(getPlayerName(battle.winner1Tag_id)) + 1

    def updatePlayerRanking(player, opponent, ranking_data):
        player_list = playerToList(players[player])
        opponent_name = getPlayerName(opponent)
        player_list[opponent_name] = player_list.get(opponent_name, 0) + 1
        opponent_list = playerToList(players[opponent])
        opponent_list[getPlayerName(player)] = opponent_list.get(getPlayerName(player), 0) + 1
    
    def generate2v2Ranking():
        for battle in Battles.objects.all():
            if battle.gameMode.startswith('TeamVsTeam') and battle.gameMode.endswith('Friendly'):
                if battle.winner1Tag_id in players:
                    if battle.winner1Tag_id == battle.opponent1Tag_id and battle.opponent2Tag_id in players:
                        updatePlayerRanking(battle.winner1Tag_id, battle.opponent2Tag_id, players)
                    elif battle.winner1Tag_id == battle.opponent2Tag_id and battle.opponent1Tag_id in players:
                        updatePlayerRanking(battle.winner1Tag_id, battle.opponent1Tag_id, players)
                    elif battle.winner1Tag_id == battle.team1Tag_id and battle.team2Tag_id in players:
                        updatePlayerRanking(battle.winner1Tag_id, battle.team2Tag_id, players)
                    elif battle.winner1Tag_id == battle.team2Tag_id and battle.team1Tag_id in players:
                        updatePlayerRanking(battle.winner1Tag_id, battle.team1Tag_id, players)

    generate2v2Ranking()
    
    template = loader.get_template("2v2.html")
    context = {
        "Will": Will,
        "Ed": Ed,
        "Godet": Godet,
        "Alex": Alex,
        "Gui": Gui
    }
    return HttpResponse(template.render(context, request))
