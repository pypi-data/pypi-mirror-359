"""Parse remaining time string"""

import re
from datetime import timedelta


def parse_next_vulnerability(vulnerable_string: str) -> timedelta:
    """
    Parses a skyhook vulnerability string and returns the timedelta before it is vulnerable
    Format is something like: Secure (vulnerable in 2d 5h 52m)
    """

    match = re.match(
        r"Secure \(vulnerable in( (?P<num_days>\d)d)?( (?P<num_hours>\d+)h)?( (?P<num_minutes>\d+)m)?\)",
        vulnerable_string,
    )

    if num_days := match.groupdict()["num_days"]:
        remaining_days = int(num_days)
    else:
        remaining_days = 0

    if num_hours := match.groupdict()["num_hours"]:
        remaining_hours = int(num_hours)
    else:
        remaining_hours = 0

    if num_min := match.groupdict()["num_minutes"]:
        remaining_minutes = int(num_min)
    else:
        remaining_minutes = 0

    return timedelta(
        days=remaining_days, hours=remaining_hours, minutes=remaining_minutes
    )
