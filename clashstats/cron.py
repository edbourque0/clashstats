import logging
import os
from django.conf import settings
from dotenv import load_dotenv
from .refreshclan import refreshclanfcn

logger = logging.getLogger(__name__)
load_dotenv()
url = "https://api.clashroyale.com/v1/"


def _get_headers():
    api_key = os.getenv("CLASH_API_KEY")
    if not api_key:
        logger.error("CLASH_API_KEY not set; cannot refresh clan.")
        return None
    return {"Authorization": f"Bearer {api_key}"}


def refresh_default_clan():
    clantag = os.getenv("REFRESH_CLAN_TAG")
    if not clantag:
        logger.warning("No clan tag configured; skipping refresh.")
        return

    headers = _get_headers()
    if not headers:
        return

    logger.info("Refreshing clan %s via refreshclanfcn", clantag)
    refreshclanfcn(clantag, url, headers, source="cron")
    logger.info("Clan %s refresh complete", clantag)
