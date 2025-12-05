from .models import BattleLogs, Members
import hashlib
import requests
import json


def create_battlelog(playertag, url, headers):
    """
    Handles a request to add battle logs to the database. This function fetches battle details
    from the Clash Royale API based on a player's tag provided in an HTTP POST request. It
    extracts and processes relevant battles to identify winners and losers for each eligible
    battle log. Validated and structured battle logs are stored in the database if unique.

    Note:
        Only POST requests are allowed. The function interacts with external APIs and the
        database.

    :param playertag: The tag of the player whose battle logs are to be fetched.
    :type playertag: str
    :param url: The base URL for the Clash Royale API.
    :type url: str
    :param headers: The headers to use for the API request.
    :type headers: dict

    :return: A JSON response with a success message if battles are added successfully or an
        error message for unsupported HTTP methods.
    :rtype: JsonResponse
    """

    r = requests.get(url=f"{url}players/%23{playertag[1:]}/battlelog", headers=headers)
    battles = r.json()

    for battle in battles:
        if len(battle["team"]) == 2:
            if battle["type"] == "clanMate2v2":
                winners_losers = define_winners_losers(battle)
                if not BattleLogs.objects.filter(id=winners_losers["hash"]).exists():
                    BattleLogs.objects.create(
                        id=winners_losers["hash"],
                        battleTime=battle["battleTime"],
                        winner1=Members.objects.get(tag=winners_losers["winner1"]),
                        winner2=Members.objects.get(tag=winners_losers["winner2"]),
                        loser1=Members.objects.get(tag=winners_losers["loser1"]),
                        loser2=Members.objects.get(tag=winners_losers["loser2"]),
                    )


def define_winners_losers(battle):
    """
    Determines the winners and losers of a battle
    Args:
        battle (dict): JSON of the battle returned by the Clash Royale API
    """
    team1_crowns = battle["team"][0]["crowns"]
    team2_crowns = battle["opponent"][0]["crowns"]

    if team1_crowns > team2_crowns:
        winners_losers = {
            "winner1": battle["team"][0]["tag"],
            "winner2": battle["team"][1]["tag"],
            "loser1": battle["opponent"][0]["tag"],
            "loser2": battle["opponent"][1]["tag"],
            "time": battle["battleTime"],
        }

        h = hashlib.sha256(
            json.dumps(winners_losers, separators=(",", ":"), sort_keys=True).encode(
                "utf-8"
            )
        ).hexdigest()
        winners_losers["hash"] = h

        return winners_losers

    else:
        winners_losers = {
            "winner1": battle["opponent"][0]["tag"],
            "winner2": battle["opponent"][1]["tag"],
            "loser1": battle["team"][0]["tag"],
            "loser2": battle["team"][1]["tag"],
            "time": battle["battleTime"],
        }

        h = hashlib.sha256(
            json.dumps(winners_losers, separators=(",", ":"), sort_keys=True).encode(
                "utf-8"
            )
        ).hexdigest()
        winners_losers["hash"] = h

        return winners_losers
