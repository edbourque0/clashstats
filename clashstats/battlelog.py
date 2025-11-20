from .models import BattleLogs, Members
import hashlib
import requests
import json


def createbattlelog(playertag, url, headers):
    """
    Handles a request to add battle logs to the database. This function fetches battle details
    from the Clash Royale API based on a player's tag provided in an HTTP POST request. It
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

    r = requests.get(url=f"{url}players/%23{playertag[1:]}/battlelog", headers=headers)
    battles = r.json()

    for battle in battles:
        if len(battle["team"]) == 2:

            if battle["type"] == "clanMate2v2":
                winlose = defineWinnersLosers(battle)

                if not BattleLogs.objects.filter(id=winlose["hash"]).exists():
                    BattleLogs.objects.create(
                        id=winlose["hash"],
                        type=battle["type"],
                        battleTime=battle["battleTime"],
                        gameMode=battle["gameMode"]["name"],
                        winner1=Members.objects.get(tag=winlose["winner1"]),
                        winner2=Members.objects.get(tag=winlose["winner2"]),
                        loser1=Members.objects.get(tag=winlose["loser1"]),
                        loser2=Members.objects.get(tag=winlose["loser2"]),
                    )


def defineWinnersLosers(battle):
    """
    This function determines the winners and losers of a battle
    Args:
        battle (dict): json of the battle returned by the Clash Royale API
    """
    team1crowns = battle["team"][0]["crowns"]
    team2crowns = battle["opponent"][0]["crowns"]

    if team1crowns > team2crowns:
        winnersandlosers = {
            "winner1": battle["team"][0]["tag"],
            "winner2": battle["team"][1]["tag"],
            "loser1": battle["opponent"][0]["tag"],
            "loser2": battle["opponent"][1]["tag"],
            "time": battle["battleTime"],
        }

        h = hashlib.sha256(
            json.dumps(winnersandlosers, separators=(",", ":"), sort_keys=True).encode(
                "utf-8"
            )
        ).hexdigest()
        winnersandlosers["hash"] = h

        return winnersandlosers

    else:
        winnersandlosers = {
            "winner1": battle["opponent"][0]["tag"],
            "winner2": battle["opponent"][1]["tag"],
            "loser1": battle["team"][0]["tag"],
            "loser2": battle["team"][1]["tag"],
            "time": battle["battleTime"],
        }

        h = hashlib.sha256(
            json.dumps(winnersandlosers, separators=(",", ":"), sort_keys=True).encode(
                "utf-8"
            )
        ).hexdigest()
        winnersandlosers["hash"] = h

        return winnersandlosers
