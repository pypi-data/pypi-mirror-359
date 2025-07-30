from django.test import TestCase
from eveuniverse.models import EveSolarSystem
from eveuniverse.tools.testdata import ModelSpec, create_testdata

from . import test_data_filename


class CreateEveUniverseTestData(TestCase):
    def test_create_testdata(self):
        moon_goo_id_range = [i for i in range(16633, 16654)]
        moon_goo_id_range.remove(16645)  # why does this one not exists? #CCPLZ
        testdata_spec = [
            ModelSpec(
                "EveConstellation",
                ids=[20000300],
                include_children=True,
                enabled_sections=[EveSolarSystem.Section.PLANETS],
            ),  # S4GH-I const in Pure Blind
            ModelSpec(
                "EveType",
                ids=[81080],
            ),  # Orbital Skyhook
        ]
        create_testdata(testdata_spec, test_data_filename())
