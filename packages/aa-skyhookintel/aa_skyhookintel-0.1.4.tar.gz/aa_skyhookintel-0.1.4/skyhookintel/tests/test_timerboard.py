from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from eveuniverse.models import EvePlanet

from allianceauth.eveonline.models import EveCorporationInfo
from allianceauth.timerboard.models import Timer

from skyhookintel.models import Skyhook, SkyhookOwner
from skyhookintel.tasks import load_solar_system_skyhooks
from skyhookintel.tests.testdata.load_eveuniverse import load_eveuniverse
from skyhookintel.thirdparty.timerboard import create_timerboard_timer


class TestTimerboard(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_eveuniverse()

    def test_create_timer_timerboard(self):
        load_solar_system_skyhooks(30002039)
        rqh_v, _ = EvePlanet.objects.get_or_create_esi(id=40130172)
        skyhook = Skyhook.objects.all()[0]

        eve_corporation = EveCorporationInfo.objects.create_corporation(109299958)
        skyhook_owner = SkyhookOwner.objects.create(corporation_info=eve_corporation)
        next_timer = timezone.now() + timedelta(days=1)

        skyhook.owner = skyhook_owner
        skyhook.next_timer = next_timer
        skyhook.save()

        create_timerboard_timer(skyhook)

        timer = Timer.objects.all()[0]

        self.assertEqual(timer.details, "Automatically created from skyhook intel.")
        self.assertEqual(timer.system, "RQH-MY")
        self.assertEqual(timer.planet_moon, "RQH-MY V")
        self.assertEqual(timer.structure, Timer.Structure.ORBITALSKYHOOK)
        self.assertEqual(timer.timer_type, Timer.TimerType.UNSPECIFIED)
        self.assertEqual(timer.objective, Timer.Objective.NEUTRAL)
        self.assertEqual(timer.eve_time, next_timer)
        self.assertFalse(timer.important)
        self.assertIsNone(timer.eve_character)
        self.assertEqual(timer.eve_corp, eve_corporation)
        self.assertFalse(timer.corp_timer)
        self.assertIsNone(timer.user)

    def test_error_on_no_owner_skyhook(self):
        load_solar_system_skyhooks(30002039)
        rqh_v, _ = EvePlanet.objects.get_or_create_esi(id=40130172)
        skyhook = Skyhook.objects.all()[0]

        next_timer = timezone.now() + timedelta(days=1)
        skyhook.next_timer = next_timer
        skyhook.save()

        self.assertRaises(AttributeError, create_timerboard_timer, skyhook)

    @patch("skyhookintel.tasks.app_labels")
    def test_no_error_on_task(self, app_labels_mock):
        # mocking the labels to avoid starting the structuretimer code
        app_labels_mock.return_value = ["timberboard"]

        load_solar_system_skyhooks(30002039)
        rqh_v, _ = EvePlanet.objects.get_or_create_esi(id=40130172)
        skyhook = Skyhook.objects.all()[0]

        next_timer = timezone.now() + timedelta(days=1)
        skyhook.next_timer = next_timer
        skyhook.save()
