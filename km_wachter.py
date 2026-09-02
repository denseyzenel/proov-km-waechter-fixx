# km_wachter.py
# KM-Waechter decides when a Vossberg Mobility car needs a service.
# Written in 2013. Modernized 2024.

SERVICE_INTERVAL_KM = 15000
WARN_AT_PERCENT = 80


def wear_percent(km_since_service: float, interval: float) -> float:
    """Return wear as a percentage of one service interval (0–100+).

    Uses true division so a car at 14,900 of 15,000 km correctly
    reports ~99.3%, not 0%.
    """
    return (km_since_service / interval) * 100


def needs_service(car: dict) -> bool:
    """Return True if the car has reached the warning threshold.

    A missing 'last_service_km' key means the reading was never recorded,
    not that the car was serviced at odometer 0.  We default to the current
    odometer so km_since = 0 and the car is treated as freshly serviced.
    """
    last = car.get("last_service_km", car["odometer"])
    km_since = car["odometer"] - last
    pct = wear_percent(km_since, SERVICE_INTERVAL_KM)
    return pct >= WARN_AT_PERCENT


def check_fleet(fleet: list) -> list:
    """Flag every car that needs service and return their IDs."""
    flagged = []
    for car in fleet:
        if needs_service(car):
            flagged.append(car["id"])
            print(f"SERVICE DUE: {car['id']}")
    return flagged
