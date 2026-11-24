import datetime

ALLOWED_KEYS = {
    "flight_id", "origin", "destination",
    "departure_datetime", "arrival_datetime",
    "price", "min_price", "sort_by", "order", "limit"
}

RECORD_KEYS = {
    "flight_id", "origin", "destination",
    "departure_datetime", "arrival_datetime", "price"
}


def _validate_datetime_str(dt_str: str) -> bool:
    if not isinstance(dt_str, str) or len(dt_str) != 16 or dt_str[10] != " ":
        return False
    try:
        dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        return dt.strftime("%Y-%m-%d %H:%M") == dt_str
    except ValueError:
        return False


def _is_valid_query(query: dict) -> bool:
    if not isinstance(query, dict):
        return False

    for k in query.keys():
        if k not in ALLOWED_KEYS:
            return False

    
    if "flight_id" in query and (not isinstance(query["flight_id"], str) or isinstance(query["flight_id"], bool)):
        return False
    if "origin" in query and (not isinstance(query["origin"], str) or isinstance(query["origin"], bool)):
        return False
    if "destination" in query and (not isinstance(query["destination"], str) or isinstance(query["destination"], bool)):
        return False

    if "departure_datetime" in query and not _validate_datetime_str(query["departure_datetime"]):
        return False
    if "arrival_datetime" in query and not _validate_datetime_str(query["arrival_datetime"]):
        return False

    if "price" in query:
        if isinstance(query["price"], bool) or not isinstance(query["price"], (int, float)):
            return False
    if "min_price" in query:
        if isinstance(query["min_price"], bool) or not isinstance(query["min_price"], (int, float)):
            return False

    if "sort_by" in query:
        if query["sort_by"] not in RECORD_KEYS:
            return False
    if "order" in query:
        if "sort_by" not in query:
            return False
        if query["order"] not in ("asc", "desc"):
            return False

    if "limit" in query:
        if isinstance(query["limit"], bool) or not isinstance(query["limit"], int) or query["limit"] < 0:
            return False

    return True


def run_query(db: list[dict], query: dict) -> dict:
    """Return one response entry for one query object."""
    if not _is_valid_query(query):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    matches = list(db)

    
    if "flight_id" in query:
        matches = [f for f in matches if f["flight_id"] == query["flight_id"]]
    if "origin" in query:
        matches = [f for f in matches if f["origin"] == query["origin"]]
    if "destination" in query:
        matches = [f for f in matches if f["destination"] == query["destination"]]
    if "departure_datetime" in query:
        matches = [f for f in matches if f["departure_datetime"] >= query["departure_datetime"]]
    if "arrival_datetime" in query:
        matches = [f for f in matches if f["arrival_datetime"] <= query["arrival_datetime"]]
    if "price" in query:
        matches = [f for f in matches if f["price"] <= query["price"]]
    if "min_price" in query:
        matches = [f for f in matches if f["price"] >= query["min_price"]]  

    
    if "sort_by" in query:
        key = query["sort_by"]
        reverse = query.get("order") == "desc"
        matches = sorted(matches, key=lambda x: x[key], reverse=reverse)

    
    if "limit" in query:
        matches = matches[:query["limit"]]

    return {"query": query, "matches": matches}


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    """Accept one query object or a list of them; always return a list."""
    if isinstance(queries, dict):
        queries = [queries]
    if not isinstance(queries, list):
        return []
    return [run_query(db, q) for q in queries]