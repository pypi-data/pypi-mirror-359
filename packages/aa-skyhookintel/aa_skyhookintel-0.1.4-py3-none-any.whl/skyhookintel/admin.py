"""Admin site."""

from django.contrib import admin
from django.utils import timezone

from skyhookintel.models import Skyhook, SkyhookOwner


@admin.register(SkyhookOwner)
class SkyhookOwnerAdmin(admin.ModelAdmin):
    list_display = ["corporation_info", "standings"]
    list_filter = ["standings"]


@admin.register(Skyhook)
class SkyhookAdmin(admin.ModelAdmin):
    list_display = ["planet", "planet_type", "owner", "next_timer_display"]
    # TODO filter only by constellations with skyhooks
    list_filter = [
        "planet_type",
        "planet__eve_solar_system__eve_constellation",
        "owner",
    ]
    fields = [("planet", "planet_type"), ("owner",), ("next_timer",)]
    readonly_fields = ["planet", "planet_type"]
    search_fields = ["planet__name", "owner__corporation_info__corporation_name"]

    def has_add_permission(self, request):
        return False

    @admin.display(description="Next timer", ordering="next_timer")
    def next_timer_display(self, skyhook: Skyhook):
        """Only returns a timer if it's in the future. Otherwise, returns None"""
        now = timezone.now()
        if timer := skyhook.next_timer:
            if timer > now:
                return timer

        return None
