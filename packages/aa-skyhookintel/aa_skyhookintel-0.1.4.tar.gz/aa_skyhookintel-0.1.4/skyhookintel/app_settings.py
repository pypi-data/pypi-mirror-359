"""App settings."""

from app_utils.app_settings import clean_setting

ICE_PLANET_TYPE_ID = 12
LAVA_PLANET_TYPE_ID = 2015

SKYHOOK_INTEL_POPULATE_TIMERBOARDS = clean_setting(
    "SKYHOOK_INTEL_POPULATE_TIMERBOARDS", True
)
