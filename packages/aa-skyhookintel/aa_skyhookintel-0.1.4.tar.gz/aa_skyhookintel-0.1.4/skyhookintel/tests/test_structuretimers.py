from datetime import timedelta

from structuretimers.models import Timer

from django.test import TestCase
from django.utils import timezone
from eveuniverse.models import EvePlanet, EveType

from allianceauth.eveonline.models import EveCorporationInfo

from skyhookintel.models import Skyhook, SkyhookOwner
from skyhookintel.tasks import load_solar_system_skyhooks, try_add_timer_to_timerboards

from ..thirdparty.structuretimers import create_structuretimers_timer
from .testdata.load_eveuniverse import load_eveuniverse


class TestStructureTimers(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_eveuniverse()

    def setUp(self):
        load_solar_system_skyhooks(30002039)
        self.rqh_v, _ = EvePlanet.objects.get_or_create_esi(id=40130172)
        self.skyhook = Skyhook.objects.all()[0]

        eve_corporation = EveCorporationInfo.objects.create_corporation(109299958)
        skyhook_owner = SkyhookOwner.objects.create(corporation_info=eve_corporation)
        self.next_timer = timezone.now() + timedelta(days=1)

        self.skyhook.owner = skyhook_owner
        self.skyhook.next_timer = self.next_timer
        self.skyhook.save()

    def test_create_timer_timerboard(self):
        create_structuretimers_timer(self.skyhook)

        timer = Timer.objects.all()[0]

        self.assertEqual(self.next_timer, timer.date)
        self.assertIsNone(timer.details_image_url)
        self.assertEqual(
            timer.details_notes, "Automatically created from skyhook intel."
        )
        self.assertIsNone(timer.eve_alliance)
        self.assertIsNone(timer.eve_character)
        self.assertIsNone(timer.eve_corporation)
        self.assertEqual(timer.eve_solar_system, self.rqh_v.eve_solar_system)
        self.assertFalse(timer.is_important)
        self.assertFalse(timer.is_opsec)
        self.assertEqual(timer.location_details, "RQH-MY V")
        self.assertEqual(timer.objective, Timer.Objective.NEUTRAL)
        self.assertEqual(timer.owner_name, "C C P")
        self.assertEqual(
            timer.structure_type, EveType.objects.get_or_create_esi(id=81080)[0]
        )
        self.assertEqual(timer.structure_name, "")
        self.assertEqual(timer.timer_type, Timer.Type.THEFT)
        self.assertEqual(timer.visibility, Timer.Visibility.UNRESTRICTED)

    def test_try_add_timer_to_timerboards(self):

        try_add_timer_to_timerboards(self.skyhook.planet.id)
