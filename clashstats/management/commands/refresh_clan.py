from django.core.management.base import BaseCommand
from clashstats.cron import refresh_default_clan
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Refresh default clan data from Clash Royale API"

    def handle(self, *args, **options):
        self.stdout.write("Starting clan refresh...")
        try:
            refresh_default_clan()
            self.stdout.write(self.style.SUCCESS("Successfully refreshed clan data"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error refreshing clan: {e}"))
            logger.error(f"Cron job error: {e}", exc_info=True)
