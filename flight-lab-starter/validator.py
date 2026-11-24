import datetime
import math
import re


FLIGHT_ID_PATTERN = re.compile(r"^[A-Za-z0-9]{2,8}$")


AIRPORT_CODE_PATTERN = re.compile(r"^[A-Z]{3}$")


def load_airports(path: str) -> set[str]:
    """Read an airport list file and return the set of codes."""
    airports = set()
    with open(path, mode="r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            airports.add(stripped)
    return airports


def _parse_strict_datetime(dt_str: str) -> datetime.datetime | None:
    """Vérification stricte de YYYY-MM-DD HH:MM avec 24-hour et zero-padded."""
    if len(dt_str) != 16 or dt_str[10] != " ":
        return None
    try:
        dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        if dt.strftime("%Y-%m-%d %H:%M") != dt_str:
            return None
        return dt
    except ValueError:
        return None


def validate_row(fields: list[str], airports: set[str]) -> str | None:
    """Check one CSV row according to checks 1 to 11."""
    
    if len(fields) != 6:
        return "WRONG_FIELD_COUNT"

    stripped_fields = [f.strip() for f in fields]

    
    if any(f == "" for f in stripped_fields):
        return "MISSING_FIELD"

    flight_id, origin, destination, dep_str, arr_str, price_str = stripped_fields

    
    if not FLIGHT_ID_PATTERN.match(flight_id):
        return "INVALID_FLIGHT_ID"

    
    if not AIRPORT_CODE_PATTERN.match(origin) or origin not in airports:
        return "INVALID_ORIGIN"

    
    if not AIRPORT_CODE_PATTERN.match(destination) or destination not in airports:
        return "INVALID_DESTINATION"

    
    if origin == destination:
        return "SAME_ORIGIN_DESTINATION"

    
    dep_dt = _parse_strict_datetime(dep_str)
    if dep_dt is None:
        return "INVALID_DEPARTURE"

    
    arr_dt = _parse_strict_datetime(arr_str)
    if arr_dt is None:
        return "INVALID_ARRIVAL"

    
    if arr_dt <= dep_dt:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"

    
    try:
        price = float(price_str)
        if math.isnan(price) or math.isinf(price):
            return "INVALID_PRICE"
    except ValueError:
        return "INVALID_PRICE"

    
    if price <= 0:
        return "NON_POSITIVE_PRICE"

    return None


def to_record(fields: list[str]) -> dict:
    """Turn a valid row into a flight record dictionary."""
    stripped = [f.strip() for f in fields]
    return {
        "flight_id": stripped[0],
        "origin": stripped[1],
        "destination": stripped[2],
        "departure_datetime": stripped[3],
        "arrival_datetime": stripped[4],
        "price": float(stripped[5]),
    }