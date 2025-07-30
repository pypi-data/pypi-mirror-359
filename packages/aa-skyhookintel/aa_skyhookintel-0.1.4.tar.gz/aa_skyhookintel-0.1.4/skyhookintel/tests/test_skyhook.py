from datetime import datetime, timedelta, timezone

from django.test import TestCase
from eveuniverse.models import EvePlanet

from skyhookintel.models import Skyhook
from skyhookintel.tasks import (
    load_constellation_id_skyhooks,
    load_solar_system_skyhooks,
)
from skyhookintel.tests.testdata.load_eveuniverse import load_eveuniverse


class TestRegex(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_eveuniverse()

    def test_create(self):
        rqh_v, _ = EvePlanet.objects.get_or_create_esi(id=40130172)

        Skyhook.create(rqh_v, Skyhook.PlanetType.ICE)

        skyhook = Skyhook.objects.all()[0]

        self.assertEqual(skyhook.planet, rqh_v)
        self.assertEqual(skyhook.planet_type, Skyhook.PlanetType.ICE)

    def test_load_solar_system(self):
        load_solar_system_skyhooks(30002039)

        rqh_v, _ = EvePlanet.objects.get_or_create_esi(id=40130172)

        skyhook = Skyhook.objects.all()[0]

        self.assertEqual(skyhook.planet, rqh_v)
        self.assertEqual(skyhook.planet_type, Skyhook.PlanetType.ICE)

    def test_load_solar_system_2_skyhooks(self):
        load_solar_system_skyhooks(30002035)

        mq_iv, _ = EvePlanet.objects.get_or_create_esi(id=40129895)
        mq_v, _ = EvePlanet.objects.get_or_create_esi(id=40129898)

        self.assertEqual(Skyhook.objects.count(), 2)

        skyhook_mq_iv = Skyhook.objects.get(planet=mq_iv)
        self.assertEqual(skyhook_mq_iv.planet_type, Skyhook.PlanetType.LAVA)

        skyhook_mq_v = Skyhook.objects.get(planet=mq_v)
        self.assertEqual(skyhook_mq_v.planet_type, Skyhook.PlanetType.ICE)

    def test_load_constellation(self):
        load_constellation_id_skyhooks(20000300)

        self.assertEqual(Skyhook.objects.count(), 9)

    def test_timers_in_1_hour(self):
        load_constellation_id_skyhooks(20000300)

        mq_iv, _ = EvePlanet.objects.get_or_create_esi(id=40129895)
        mq_v, _ = EvePlanet.objects.get_or_create_esi(id=40129898)
        rqh_v, _ = EvePlanet.objects.get_or_create_esi(id=40130172)
        tfa_ii, _ = EvePlanet.objects.get_or_create_esi(id=40130044)
        tfa_iii, _ = EvePlanet.objects.get_or_create_esi(id=40130047)

        skyhook_mq_iv = Skyhook.objects.get(planet=mq_iv)
        skyhook_mq_v = Skyhook.objects.get(planet=mq_v)
        skyhook_rq_v = Skyhook.objects.get(planet=rqh_v)
        skyhook_tfa_ii = Skyhook.objects.get(planet=tfa_ii)
        skyhook_tfa_iii = Skyhook.objects.get(planet=tfa_iii)

        skyhook_mq_iv.add_timer(timedelta(minutes=20))
        skyhook_mq_v.add_timer(timedelta(minutes=55))
        skyhook_rq_v.add_timer(timedelta(hours=3))

        skyhook_next_hour = Skyhook.get_next_hour_skyhooks()

        self.assertIn(skyhook_mq_iv, skyhook_next_hour)
        self.assertIn(skyhook_mq_v, skyhook_next_hour)
        self.assertNotIn(skyhook_rq_v, skyhook_next_hour)
        self.assertNotIn(skyhook_tfa_ii, skyhook_next_hour)
        self.assertNotIn(skyhook_tfa_iii, skyhook_next_hour)

    def test_past_next_timer(self):
        load_constellation_id_skyhooks(20000300)

        mq_iv, _ = EvePlanet.objects.get_or_create_esi(id=40129895)
        mq_v, _ = EvePlanet.objects.get_or_create_esi(id=40129898)
        skyhook_mq_iv = Skyhook.objects.get(planet=mq_iv)
        skyhook_mq_v = Skyhook.objects.get(planet=mq_v)

        skyhook_mq_iv.next_timer = datetime(
            2020, 10, 12, tzinfo=timezone.utc
        )  # long in the past
        skyhook_mq_iv.save()

        self.assertTrue(skyhook_mq_iv.is_timer_passed())

        skyhook_mq_v.next_timer = datetime(
            2050, 10, 5, tzinfo=timezone.utc
        )  # long in the future
        skyhook_mq_v.save()

        self.assertFalse(skyhook_mq_v.is_timer_passed())
