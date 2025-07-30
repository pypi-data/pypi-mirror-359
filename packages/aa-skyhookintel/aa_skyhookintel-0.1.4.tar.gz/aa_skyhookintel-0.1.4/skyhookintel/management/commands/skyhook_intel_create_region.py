from django.core.management.base import BaseCommand

from allianceauth.services.hooks import get_extension_logger

from skyhookintel.tasks import load_region_id_skyhooks

logger = get_extension_logger(__name__)


class Command(BaseCommand):
    help = "Creates a skyhook for every magma/ice planet in the region with the given region"

    def add_arguments(self, parser):
        parser.add_argument("region_id", type=int)

    def handle(self, *args, **options):
        region_id = options["region_id"]
        logger.info("Starting task to load skyhooks in region id %s", region_id)
        load_region_id_skyhooks.delay(region_id)
