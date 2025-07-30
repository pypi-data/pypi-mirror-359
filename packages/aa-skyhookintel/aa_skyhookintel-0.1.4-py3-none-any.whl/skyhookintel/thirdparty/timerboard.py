"""
Handles interactions with the timerboard application

https://allianceauth.readthedocs.io/en/v4.6.1/features/apps/timerboard.html
"""

from allianceauth.timerboard.models import Timer

from skyhookintel.models import Skyhook, SkyhookOwner


def create_timerboard_timer(skyhook: Skyhook):
    """
    Adds a timer in the timerboard application for the given skyhook
    """

    Timer.objects.create(
        details="Automatically created from skyhook intel.",
        system=skyhook.planet.eve_solar_system.name,
        planet_moon=skyhook.planet,
        structure=Timer.Structure.ORBITALSKYHOOK,
        timer_type=Timer.TimerType.UNSPECIFIED,
        objective=match_objective(skyhook),
        eve_time=skyhook.next_timer,
        eve_corp=skyhook.owner.corporation_info,
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

    return Timer.Objective.NEUTRAL
