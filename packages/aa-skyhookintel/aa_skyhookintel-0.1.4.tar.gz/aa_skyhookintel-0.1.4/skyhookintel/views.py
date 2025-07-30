"""Views."""

from abc import ABC, abstractmethod
from datetime import timedelta

from django_datatables_view.base_datatable_view import BaseDatatableView

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db import models
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from allianceauth.eveonline.evelinks import dotlan
from allianceauth.services.hooks import get_extension_logger
from app_utils.views import link_html

from skyhookintel.app_settings import SKYHOOK_INTEL_POPULATE_TIMERBOARDS
from skyhookintel.models import Skyhook, SkyhookOwner
from skyhookintel.regex import parse_next_vulnerability
from skyhookintel.tasks import try_add_timer_to_timerboards

logger = get_extension_logger(__name__)


@login_required
@permission_required("skyhookintel.basic_access")
def index(request):
    """Render index view."""
    return redirect("skyhookintel:upcoming_timers")


@permission_required("skyhookintel.editor")
def add_skyhook_timer(request, planet_id: int):
    """Add a skyhook timer"""
    skyhook = get_object_or_404(Skyhook, planet_id=planet_id)

    if not skyhook.is_timer_passed():
        return redirect("skyhookintel:index")

    if request.method == "POST":
        if request_type := request.POST.get("type"):
            match request_type:
                case "regex":
                    vuln_string = request.POST.get("vuln_string")
                    logger.debug("Parsing regex for %s", vuln_string)
                    delta = parse_next_vulnerability(vuln_string)
                case "input":
                    delta = timedelta(
                        days=int(request.POST.get("vuln_days")),
                        hours=int(request.POST.get("vuln_hours")),
                        minutes=int(request.POST.get("vuln_minutes")),
                    )
                case _:
                    logger.warning(
                        "Invalid new skyhook timer request received from user %s",
                        request.user,
                    )
                    messages.error(request, _("Something went wrong"))
                    return redirect("skyhookintel:index")

            logger.debug("Adding new timer to skyhook %s in %s", skyhook, delta)
            skyhook.add_timer(delta)

            if SKYHOOK_INTEL_POPULATE_TIMERBOARDS:
                try_add_timer_to_timerboards.delay(skyhook.planet.id)

            return render(request, "skyhookintel/close_page.html")

    return render(
        request,
        "skyhookintel/add_timer.html",
        {
            "skyhook": skyhook,
        },
    )


@login_required
@permission_required("skyhookintel.basic_access")
def upcoming_timers(request):
    """Displays upcoming skyhook timers"""
    return render(request, "skyhookintel/upcoming.html")


@login_required
@permission_required("skyhookintel.editor")
def no_timers(request):
    """Displays skyhooks without timers"""
    return render(request, "skyhookintel/no_timers.html")


# pylint: disable = too-many-ancestors
class ABSSkyhookListJson(
    PermissionRequiredMixin, LoginRequiredMixin, BaseDatatableView, ABC
):
    """Abstract class to query the Skyhooks for datatables"""

    model = Skyhook

    order_columns = [
        "next_timer",
        "pk",
        "",
        "",
        "",
        "",
        "",
        "",
    ]

    @abstractmethod
    def get_region_index(self) -> int:
        """Returns the index of the region in the datatable"""

    @abstractmethod
    def get_constellation_index(self) -> int:
        """Returns the index of the constellation in the datatable"""

    @abstractmethod
    def get_system_index(self) -> int:
        """Returns the index of the system in the datatable"""

    @abstractmethod
    def get_standings_index(self) -> int:
        """Return the index of the standings in the datatable"""

    # pylint: disable = too-many-return-statements
    def render_column(self, row: Skyhook, column):
        if column == "id":
            return row.pk

        if column == "planet_name":
            return row.planet.name

        if column == "add_timer":
            return input_timer_button_html(row)

        if column in ["next_timer_eve", "next_timer_local"]:
            if next_timer := row.next_timer:
                return next_timer.isoformat()

        if column == "standings":
            if owner := row.owner:
                return owner.standings

        if column == "owner":
            if owner := row.owner:
                return self._render_owner(owner)

        if result := self._render_location(row, column):
            return result

        return super().render_column(row, column)

    def filter_queryset(self, qs):
        """Use params in the GET to filter"""
        qs = self._apply_search_filter(
            qs,
            1,
            "planet_type",
        )

        qs = self._apply_search_filter(
            qs,
            self.get_region_index(),
            "planet__eve_solar_system__eve_constellation__eve_region__name",
        )

        qs = self._apply_search_filter(
            qs,
            self.get_constellation_index(),
            "planet__eve_solar_system__eve_constellation__name",
        )

        qs = self._apply_search_filter(
            qs, self.get_system_index(), "planet__eve_solar_system__name"
        )

        if my_filter := self.request.GET.get(
            f"columns[{self.get_standings_index()}][search][value]", None
        ):
            if "Neutral" in my_filter:
                qs = qs.filter(
                    Q(owner__standings__iregex=my_filter) | Q(owner__isnull=True)
                )
            else:
                qs = self._apply_search_filter(
                    qs, self.get_standings_index(), "owner__standings"
                )

        if search := self.request.GET.get("search[value]", None):
            qs = qs.filter(planet__name__istartswith=search)

        return qs

    def _apply_search_filter(self, qs, column_num, field) -> models.QuerySet:
        my_filter = self.request.GET.get(f"columns[{column_num}][search][value]", None)
        if my_filter:
            if self.request.GET.get(f"columns[{column_num}][search][regex]", False):
                kwargs = {f"{field}__iregex": my_filter}
            else:
                kwargs = {f"{field}__istartswith": my_filter}
            return qs.filter(**kwargs)
        return qs

    def _render_location(self, row: Skyhook, column):
        solar_system = row.planet.eve_solar_system
        if solar_system.is_high_sec:
            sec_class = "text-high-sec"
        elif solar_system.is_low_sec:
            sec_class = "text-low-sec"
        else:
            sec_class = "text-null-sec"
        solar_system_link = format_html(
            '{}&nbsp;<span class="{}">{}</span>',
            link_html(dotlan.solar_system_url(solar_system.name), solar_system.name),
            sec_class,
            round(solar_system.security_status, 1),
        )

        constellation = row.planet.eve_solar_system.eve_constellation
        region = constellation.eve_region
        location_html = format_html(
            "{}<br><em>{}</em>", constellation.name, region.name
        )
        # TODO check if py310 authorize match
        if column == "solar_system_name":
            return solar_system.name

        if column == "solar_system_link":
            return solar_system_link

        if column == "location_html":
            return location_html

        if column == "region_name":
            return region.name

        if column == "constellation_name":
            return constellation.name

        return None

    def _render_owner(self, owner: SkyhookOwner):
        """Renders the corporation/alliance holding the skyhook"""
        corporation = owner.corporation_info
        corporation_link = link_html(
            dotlan.corporation_url(corporation.corporation_name),
            corporation.corporation_name,
        )

        if alliance := corporation.alliance:
            alliance_link = link_html(
                dotlan.alliance_url(alliance.alliance_name), alliance.alliance_name
            )
            return format_html("{} / {}", corporation_link, alliance_link)

        return corporation_link

    # pylint: disable = arguments-differ
    @staticmethod
    @abstractmethod
    def get_initial_queryset():
        """Returns the queryset to use when working on the skyhooks"""


class UpcomingSkyhooksListJson(ABSSkyhookListJson):
    """Queries skyhooks with upcoming timers"""

    permission_required = "skyhookintel.basic_access"

    columns = [
        "id",
        "planet_name",
        "planet_type",
        "solar_system_link",
        "location_html",
        "owner",
        "next_timer_eve",
        "next_timer_local",
        "region_name",
        "constellation_name",
        "solar_system_name",
        "standings",
    ]

    def get_region_index(self) -> int:
        return 7

    def get_constellation_index(self) -> int:
        return 8

    def get_system_index(self) -> int:
        return 9

    def get_standings_index(self) -> int:
        return 10

    @staticmethod
    def get_initial_queryset():
        """Initial query"""
        return Skyhook.get_skyhooks_with_timers()


class NoTimersSkyhooksListJson(ABSSkyhookListJson):
    """Queries skyhooks without timers"""

    permission_required = "skyhookintel.editor"

    columns = [
        "id",
        "planet_name",
        "planet_type",
        "solar_system_link",
        "location_html",
        "owner",
        "add_timer",
        "region_name",
        "constellation_name",
        "solar_system_name",
        "standings",
    ]

    def get_region_index(self) -> int:
        return 6

    def get_constellation_index(self) -> int:
        return 7

    def get_system_index(self) -> int:
        return 8

    def get_standings_index(self) -> int:
        return 9

    @staticmethod
    def get_initial_queryset():
        """Initial query"""
        return Skyhook.get_skyhooks_no_timers()


def skyhooks_with_timers_fdd_data(request) -> JsonResponse:
    """List for the drop-down fields of the skyhooks with timers"""
    return skyhook_fdd_data(request, UpcomingSkyhooksListJson)


def skyhooks_no_timers_fdd_data(request) -> JsonResponse:
    """List for the  drop-down fields of no timers skyhooks"""
    return skyhook_fdd_data(request, NoTimersSkyhooksListJson)


def skyhook_fdd_data(request, skyhook_list_json: ABSSkyhookListJson) -> JsonResponse:
    """List for the drop-down fields"""
    qs = skyhook_list_json.get_initial_queryset()
    columns = request.GET.get("columns")
    result = {}
    if columns:
        for column in columns.split(","):
            options = _calc_options(request, qs, column)
            result[column] = sorted(list(set(options)), key=str.casefold)
    return JsonResponse(result, safe=False)


def _calc_options(request, qs, column):

    if column == "planet_type":
        return qs.values_list(
            "planet_type",
            flat=True,
        )

    if column == "region_name":
        return qs.values_list(
            "planet__eve_solar_system__eve_constellation__eve_region__name",
            flat=True,
        )

    if column == "constellation_name":
        return qs.values_list(
            "planet__eve_solar_system__eve_constellation__name",
            flat=True,
        )

    if column == "solar_system_name":
        return qs.values_list(
            "planet__eve_solar_system__name",
            flat=True,
        )

    if column == "standings":
        return {
            standing or "Neutral"
            for standing in qs.values_list(
                "owner__standings",
                flat=True,
            )
        }

    return [f"** ERROR: Invalid column name '{column}' **"]


def input_timer_button_html(
    skyhook: Skyhook,
) -> str:
    """
    Returns an HTML button that redirects to a page where a skyhook timer can be inputted
    """

    return format_html(
        "<a "
        "class=btn btn-primary "
        "target=_blank "
        "href={}"
        ">"
        '<i class="fas fa-clock"></i>'
        "</a>",
        reverse("skyhookintel:add_skyhook_timer", args=[skyhook.pk]),
    )
