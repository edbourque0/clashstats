import logging
import requests
from .models import Clans, Members

logger = logging.getLogger(__name__)


def create_members(clan_tag, url, headers):
    """
    Fetches and upserts clan members from the Clash Royale API.

    Fetches the Clans object once before the loop to avoid an extra DB query
    per member (previously Clans.objects.get() was called inside the loop).
    """
    try:
        r = requests.get(
            url=f"{url}clans/%23{clan_tag[1:]}/members",
            headers=headers,
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.Timeout:
        logger.error("Timeout fetching members for clan %s", clan_tag)
        return
    except requests.exceptions.RequestException as e:
        logger.error("Error fetching members for clan %s: %s", clan_tag, e)
        return

    members = data.get("items", [])

    # Fetch the clan object once before the loop instead of once per member
    try:
        clan_obj = Clans.objects.get(tag=clan_tag)
    except Clans.DoesNotExist:
        logger.error("Clan %s not found in DB; run create_clan first.", clan_tag)
        return

    for member in members:
        Members.objects.update_or_create(
            tag=member["tag"],
            defaults={
                "clanTag": clan_obj,
                "name": member["name"],
                "role": member["role"],
                "lastSeen": member["lastSeen"],
                "expLevel": member["expLevel"],
                "trophies": member["trophies"],
                "clanRank": member["clanRank"],
                "donations": member["donations"],
                "donationsReceived": member["donationsReceived"],
            },
        )
