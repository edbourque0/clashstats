import logging
import requests
from .models import Clans

logger = logging.getLogger(__name__)


def create_clan(clan_tag, url, headers):
    """
    Fetches clan data from the Clash Royale API and upserts it into the DB.
    Handles network errors gracefully rather than propagating exceptions.
    """
    try:
        r = requests.get(
            url=f"{url}clans/%23{clan_tag[1:]}",
            headers=headers,
            params={"name": clan_tag},
            timeout=10,
        )
        r.raise_for_status()
        clan = r.json()
    except requests.exceptions.Timeout:
        logger.error("Timeout fetching clan %s", clan_tag)
        return
    except requests.exceptions.RequestException as e:
        logger.error("Error fetching clan %s: %s", clan_tag, e)
        return

    Clans.objects.update_or_create(
        tag=clan["tag"],
        defaults={
            "name": clan["name"],
            "type": clan["type"],
            "badgeId": clan["badgeId"],
            "location": clan["location"]["countryCode"],
            "donationsPerWeek": clan["donationsPerWeek"],
            "members": clan["members"],
        },
    )
