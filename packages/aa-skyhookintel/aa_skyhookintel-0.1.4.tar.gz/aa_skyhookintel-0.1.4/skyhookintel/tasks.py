"""Tasks."""

from celery import shared_task

from eveuniverse.models import EveConstellation, EveRegion, EveSolarSystem

from allianceauth.services.hooks import get_extension_logger
from app_utils.django import app_labels

from skyhookintel.app_settings import ICE_PLANET_TYPE_ID, LAVA_PLANET_TYPE_ID
from skyhookintel.models import Skyhook

logger = get_extension_logger(__name__)


class NoTimerFound(Exception):
    """Raised when no timer is found for the given skyhook"""


@shared_task
def load_region_id_skyhooks(region_id: int):
    """Loads all the possible skyhooks in a region"""
    logger.info("Loading region id %s", region_id)

    region, _ = EveRegion.objects.update_or_create_esi(
        id=region_id, include_children=True
    )
    for constellation in region.eve_constellations.all():
        load_constellation_id_skyhooks.delay(constellation.id)


@shared_task
def load_constellation_id_skyhooks(constellation_id: int):
    """Load all skyhooks in the constellation"""
    logger.info("Loading constellation id %s", constellation_id)

    constellation, _ = EveConstellation.objects.update_or_create_esi(
        id=constellation_id, include_children=True
    )
    for solar_system in constellation.eve_solarsystems.all():
        if solar_system.security_status > 0.0:
            logger.info(
                "Skipping solar system id %s because the security status is %s",
                solar_system.id,
                solar_system.security_status,
            )
        load_solar_system_skyhooks.delay(solar_system.id)


@shared_task
def load_solar_system_skyhooks(solar_system_id: int):
    """Load all skyhooks in the solar system"""
    logger.info("Loading solar system %s", solar_system_id)

    solar_system, _ = EveSolarSystem.objects.update_or_create_esi(
        id=solar_system_id,
        include_children=True,
        enabled_sections=[EveSolarSystem.Section.PLANETS],
    )

    for planet in solar_system.eve_planets.filter(eve_type__id=LAVA_PLANET_TYPE_ID):
        Skyhook.create(planet, Skyhook.PlanetType.LAVA)

    for planet in solar_system.eve_planets.filter(eve_type__id=ICE_PLANET_TYPE_ID):
        Skyhook.create(planet, Skyhook.PlanetType.ICE)


@shared_task
def try_add_timer_to_timerboards(skyhook_planet_id: int):
    """Tries to find a timerboard module and add the timer to the module"""
    logger.info(
        "Trying to add a skyhook timer for skyhook with planet id %d", skyhook_planet_id
    )

    skyhook = Skyhook.objects.get(planet__id=skyhook_planet_id)

    if skyhook.is_timer_passed():
        raise NoTimerFound(f"No timer found for skyhook {skyhook} id {skyhook.id}")

    application_labels = app_labels()

    if "timerboard" in application_labels:
        if not skyhook.owner:
            logger.info(
                "Not creating a notification for skyhook id %d as no owner has been declared",
                skyhook_planet_id,
            )
            return

        from .thirdparty.timerboard import create_timerboard_timer

        create_timerboard_timer(skyhook)

    if "structuretimers" in application_labels:
        from .thirdparty.structuretimers import create_structuretimers_timer

        create_structuretimers_timer(skyhook)
