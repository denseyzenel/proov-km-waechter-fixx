# fleet_utils.py
# Shared helpers for the KM-Waechter service. Modernized 2024.
# Dead functions (parse_service_date, chunk_list) and the duplicate
# is_due() removed — they were unused since 2014.

MILES_PER_KM = 0.621371          # correct: 1 km = 0.621371 miles


def km_to_miles(km: float) -> float:
    """Convert kilometres to miles for the UK partner report."""
    return km * MILES_PER_KM


def format_number(value: float) -> str:
    """Format a float to one decimal place."""
    return f"{value:.1f}"


def format_percent(value: float) -> str:
    """Format a float as a whole-number percentage string."""
    return f"{int(value)}%"


def mean(values: list) -> float:
    """Return the arithmetic mean of a list of numbers.

    Returns 0 for an empty list.
    """
    if not values:
        return 0
    return sum(values) / len(values)
