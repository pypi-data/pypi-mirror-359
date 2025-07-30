"""
Handles interactions with the structuretimers application

https://gitlab.com/ErikKalkoken/aa-structuretimers
"""

from structuretimers.constants import EveTypeId
from structuretimers.models import Timer

from eveuniverse.models import EveType

from skyhookintel.models import Skyhook, SkyhookOwner


def create_structuretimers_timer(skyhook: Skyhook):
    """
    Adds a timer in the structuretimers application for the given skyhook
    """

    if owner := skyhook.owner:
        owner_name = owner.corporation_info.corporation_name
    else:
        owner_name = "Unknown"

    Timer.objects.create(
        date=skyhook.next_timer,
        details_notes="Automatically created from skyhook intel.",
        eve_solar_system=skyhook.planet.eve_solar_system,
        location_details=skyhook.planet.name,
        objective=match_objective(skyhook),
        owner_name=owner_name,
        structure_type=EveType.objects.get_or_create_esi(id=EveTypeId.ORBITAL_SKYHOOK)[
            0
        ],
        timer_type=Timer.Type.THEFT,
    )


def match_objective(skyhook: Skyhook) -> Timer.Objective:
    """Match the skyhook objective with a timerboard objective"""

    if owner := skyhook.owner:
        match owner.standings:
            case SkyhookOwner.Standing.FRIENDLY:
                return Timer.Objective.FRIENDLY
            case SkyhookOwner.Standing.NEUTRAL:
                return Timer.Objective.NEUTRAL
            case SkyhookOwner.Standing.HOSTILE:
                return Timer.Objective.HOSTILE

    return Timer.Objective.UNDEFINED
