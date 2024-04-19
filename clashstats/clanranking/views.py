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


def clanrankingsearch(request):
    template = loader.get_template("clanrankinghome.html")
    context = {
        "clans": Clans.objects.all(),
    }
    return HttpResponse(template.render(context, request))


@csrf_exempt
def clanrefresh(request, clantag):
    # Request variables
    APIKEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjRiODJiNzlmLTg5NzAtNDllYi05NGEyLWEyZDAzNzU5MjIyNSIsImlhdCI6MTcxMjk1MzUyMSwic3ViIjoiZGV2ZWxvcGVyLzNkNjhmM2MyLWM4ZmItNDAyYy0zZTU4LTk0YjIzMGY1Y2IzZCIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyI3NC4xMi4xNjkuMjMwIiwiMTczLjE4Mi4xNTQuMjQ2IiwiMjA5LjE3MS4xNjIuMTQ1IiwiMjA3LjE2Ny4yMTYuODkiXSwidHlwZSI6ImNsaWVudCJ9XX0.YvF3ojCgj7r7KdBBCoSufuTnVj6Qd0wz6YaRWfdSet6QPIZOn3HSlXlJUlyLLfUQUQi0G6nfL3MPleE_CTnn2w"
    headers = {
        "Authorization": "Bearer " + APIKEY,
    }
    c = requests.get(
        f"https://api.clashroyale.com/v1/clans/%23{clantag}", headers=headers
    )

    rawclan = c.json()
    for memint, member in enumerate(rawclan["memberList"]):
        if Members.objects.filter(tag=member["tag"][1:]).exists() == False:
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

    if Clans.objects.filter(tag=rawclan["tag"]).exists() == False:
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
        "today": datetime.strftime(timezone.now(), "%Y-%m-%d"),
    }
    
    default_start_date = timezone.now() - timedelta(days=7)
    default_end_date = timezone.now()

    start_date = default_start_date
    end_date = default_end_date
    
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
                print(html)
                return HttpResponse(html)
        
    return HttpResponse(template.render(context, request))
