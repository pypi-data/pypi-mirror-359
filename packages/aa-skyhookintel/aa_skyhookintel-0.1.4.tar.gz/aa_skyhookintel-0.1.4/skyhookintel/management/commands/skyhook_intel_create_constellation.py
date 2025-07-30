from django.core.management.base import BaseCommand

from allianceauth.services.hooks import get_extension_logger

from skyhookintel.tasks import load_constellation_id_skyhooks

logger = get_extension_logger(__name__)


class Command(BaseCommand):
    help = "Creates a skyhook for every magma/ice planet in the region with the given constellation"

    def add_arguments(self, parser):
        parser.add_argument("constellation_id", type=int)

    def handle(self, *args, **options):
        constellation_id = options["constellation_id"]
        logger.info(
            "Starting task to load skyhooks in constellation id %s", constellation_id
        )
        load_constellation_id_skyhooks.delay(constellation_id)
