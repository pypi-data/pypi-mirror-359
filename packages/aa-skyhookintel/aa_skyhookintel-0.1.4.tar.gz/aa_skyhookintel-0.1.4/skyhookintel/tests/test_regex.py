from datetime import timedelta

from django.test import TestCase

from skyhookintel.regex import parse_next_vulnerability


class TestRegex(TestCase):

    def test_basic(self):
        string1 = "Secure (vulnerable in 2d 5h 52m)"
        string2 = "Secure (vulnerable in 2d 15h 2m)"

        expected1 = timedelta(days=2, hours=5, minutes=52)
        expected2 = timedelta(days=2, hours=15, minutes=2)

        self.assertEqual(parse_next_vulnerability(string1), expected1)
        self.assertEqual(parse_next_vulnerability(string2), expected2)

    def test_no_days(self):
        string = "Secure (vulnerable in 5h 52m)"

        expected = timedelta(hours=5, minutes=52)

        self.assertEqual(parse_next_vulnerability(string), expected)

    def test_no_hours(self):
        string = "Secure (vulnerable in 2d 52m)"

        expected = timedelta(days=2, minutes=52)

        self.assertEqual(parse_next_vulnerability(string), expected)

    def test_no_minutes(self):
        string = "Secure (vulnerable in 2d 5h)"

        expected = timedelta(days=2, hours=5)

        self.assertEqual(parse_next_vulnerability(string), expected)
