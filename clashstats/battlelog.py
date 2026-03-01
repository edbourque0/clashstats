import hashlib
import json
import logging
import requests
from .models import BattleLogs, Members

logger = logging.getLogger(__name__)


def create_battlelog(playertag, url, headers):
    """
    Fetches and stores battle logs for a player.

    Uses batch DB operations to avoid N+1 queries:
    - One existence check across all candidate battles.
    - One member lookup for all participant tags.
    - One bulk_create for all new BattleLog rows.
    """
    try:
        r = requests.get(
            url=f"{url}players/%23{playertag[1:]}/battlelog",
            headers=headers,
            timeout=10,
        )
        r.raise_for_status()
        battles = r.json()
    except requests.exceptions.Timeout:
        logger.error("Timeout fetching battlelog for player %s", playertag)
        return
    except requests.exceptions.RequestException as e:
        logger.error("Error fetching battlelog for %s: %s", playertag, e)
        return

    # Step 1: Parse all qualifying battles in pure Python (no DB calls yet)
    candidates = []
    all_tags = set()
    for battle in battles:
        if len(battle["team"]) == 2 and battle["type"] == "clanMate2v2":
            wl = define_winners_losers(battle)
            if wl is not None:
                all_tags.update([wl["winner1"], wl["winner2"], wl["loser1"], wl["loser2"]])
                candidates.append(wl)

    if not candidates:
        return

    # Step 2: Check which hashes already exist — one query for all candidates
    existing_hashes = set(
        BattleLogs.objects
        .filter(id__in=[c["hash"] for c in candidates])
        .values_list("id", flat=True)
    )

    new_candidates = [c for c in candidates if c["hash"] not in existing_hashes]
    if not new_candidates:
        return

    # Step 3: Fetch all needed members in one query
    members_map = {
        m.tag: m
        for m in Members.objects.filter(tag__in=all_tags)
    }

    # Step 4: Build BattleLog instances; skip battles with unknown players
    to_create = []
    for wl in new_candidates:
        w1 = members_map.get(wl["winner1"])
        w2 = members_map.get(wl["winner2"])
        l1 = members_map.get(wl["loser1"])
        l2 = members_map.get(wl["loser2"])

        if not (w1 and w2 and l1 and l2):
            logger.warning(
                "Skipping battle %s: one or more players not in DB",
                wl["hash"],
            )
            continue

        to_create.append(BattleLogs(
            id=wl["hash"],
            battleTime=wl["time"],
            winner1=w1,
            winner2=w2,
            loser1=l1,
            loser2=l2,
        ))

    # Step 5: Bulk create — one INSERT statement instead of N individual inserts.
    # ignore_conflicts handles any race condition where another process inserted
    # the same hash between the existence check and this insert.
    if to_create:
        BattleLogs.objects.bulk_create(to_create, ignore_conflicts=True)


def define_winners_losers(battle):
    """
    Determines the winners and losers of a battle.
    Returns None if the game was a draw (equal crowns).
    """
    team1_crowns = battle["team"][0]["crowns"]
    team2_crowns = battle["opponent"][0]["crowns"]

    if team1_crowns == team2_crowns:
        return None

    if team1_crowns > team2_crowns:
        winners_losers = {
            "winner1": battle["team"][0]["tag"],
            "winner2": battle["team"][1]["tag"],
            "loser1":  battle["opponent"][0]["tag"],
            "loser2":  battle["opponent"][1]["tag"],
            "time":    battle["battleTime"],
        }
    else:
        winners_losers = {
            "winner1": battle["opponent"][0]["tag"],
            "winner2": battle["opponent"][1]["tag"],
            "loser1":  battle["team"][0]["tag"],
            "loser2":  battle["team"][1]["tag"],
            "time":    battle["battleTime"],
        }

    h = hashlib.sha256(
        json.dumps(winners_losers, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).hexdigest()
    winners_losers["hash"] = h
    return winners_losers
