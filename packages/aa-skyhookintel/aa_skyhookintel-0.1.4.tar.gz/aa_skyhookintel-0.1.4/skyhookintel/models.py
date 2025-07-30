"""Models."""

from datetime import timedelta

from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from eveuniverse.models import EvePlanet

from allianceauth.eveonline.models import EveCorporationInfo


class General(models.Model):
    """A meta model for app permissions."""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (
            ("basic_access", "Can access this app and see timers"),
            ("editor", "Can add new timers"),
        )


class SkyhookOwner(models.Model):
    """Represent a corporation owning a skyhook"""

    class Standing(models.TextChoices):
        """Standing of this group to the auth"""

        FRIENDLY = "Friendly", _("Friendly")
        HOSTILE = "Hostile", _("Hostile")
        NEUTRAL = "Neutral", _("Neutral")

    corporation_info = models.OneToOneField(
        EveCorporationInfo, primary_key=True, on_delete=models.CASCADE
    )
    standings = models.CharField(
        max_length=16,
        choices=Standing.choices,
        default=Standing.NEUTRAL,
        help_text=_("Standings toward this group"),
    )

    def __str__(self):
        return f"{self.corporation_info.corporation_name}"


class Skyhook(models.Model):
    """Represents a skyhook on a lava or ice planet and its timers"""

    class PlanetType(models.TextChoices):
        """Reagent producing planets"""

        LAVA = "L", _("Lava planet")
        ICE = "I", _("Ice planet")

    planet = models.OneToOneField(EvePlanet, primary_key=True, on_delete=models.CASCADE)
    planet_type = models.CharField(max_length=1, choices=PlanetType.choices)
    owner = models.ForeignKey(
        SkyhookOwner, on_delete=models.CASCADE, null=True, blank=True
    )
    next_timer = models.DateTimeField(null=True, default=None, blank=True)

    def add_timer(self, delta: timedelta):
        """Adds a timer to the skyhook"""
        timer = timezone.now() + delta
        self.next_timer = timer
        self.save()

    def is_timer_passed(self) -> bool:
        """
        Tells if a timer was in the past

        Will return true if no timer is given
        """

        if timer := self.next_timer:
            return timer < timezone.now()

        return True

    @classmethod
    def create(cls, planet: EvePlanet, planet_type: PlanetType) -> "Skyhook":
        """
        Creates a new skyhook and returns it
        If it already exists override the planet type
        """
        new_skyhook, _ = Skyhook.objects.update_or_create(
            planet=planet, defaults={"planet_type": planet_type}
        )
        return new_skyhook

    @classmethod
    def select_related(cls):
        """Returns a queryset of all skyhooks with select_related loaded"""
        return cls.objects.select_related(
            "planet",
            "planet__eve_solar_system",
            "planet__eve_solar_system__eve_constellation",
            "owner__corporation_info",
        )

    @classmethod
    def get_skyhooks_with_timers(cls):
        """
        Returns all skyhooks with a timer in the future
        """
        now = timezone.now()
        return cls.select_related().exclude(Q(next_timer=None) | Q(next_timer__lt=now))

    @classmethod
    def get_skyhooks_no_timers(cls):
        """
        Returns all skyhooks with no timer set or past timers
        """
        now = timezone.now()
        return cls.select_related().filter(Q(next_timer=None) | Q(next_timer__lt=now))

    @classmethod
    def get_skyhook_from_planet_id(cls, planet_id: int):
        """Returns the skyhook associated with the planet id"""
        return cls.objects.get(planet_id=planet_id)

    @classmethod
    def get_next_hour_skyhooks(cls):
        """Return a queryset of all skyhooks with a timer in the upcoming hour"""
        now = timezone.now()
        return cls.objects.filter(
            Q(next_timer__gt=now) & Q(next_timer__lt=now + timedelta(hours=1))
        )

    def __str__(self):
        return f"{self.planet.name} - {self.planet_type}"
