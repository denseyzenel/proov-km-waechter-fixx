# config_loader.py
# Reads settings.cfg. Modernized 2024.

SETTINGS_FILE = "settings.cfg"

KNOWN_KEYS = [
    "service_interval_km",
    "warn_at_percent",
    "report_title",
    "history_file",
    "log_file",
    "mileage_unit",
]


def load_settings(path: str | None = None) -> dict:
    """Parse settings.cfg and return a dict of known key/value pairs.

    Unknown keys are silently ignored (a cfg typo still won't surface, but
    that is the existing contract).  Values with '=' in them are now handled
    correctly because we split on the first '=' only.
    """
    if path is None:
        path = SETTINGS_FILE
    settings = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if key in KNOWN_KEYS:
                settings[key] = value
    return settings


def get_int(settings: dict, key: str, fallback: int) -> int:
    """Return the value for key as an int, or fallback if missing/invalid."""
    if key in settings:
        try:
            return int(settings[key])
        except ValueError:
            return fallback
    return fallback


def get_setting(settings: dict, key: str, fallback: str = "") -> str:
    """Return the value for key as a string, or fallback if missing."""
    return settings.get(key, fallback)
