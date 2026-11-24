import csv
import os
from validator import validate_row, to_record


def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    """Process the CSV files in the order given.

    Return (records, errors).
    """
    records: list[dict] = []
    errors: list[str] = []
    seen_flights: set[tuple[str, str]] = set()

    for path in paths:
        base_name = os.path.basename(path)
        with open(path, mode="r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            line_num = 0
            for line in f:
                line_num += 1
                raw_line = line.strip()
                # Sauter la ligne d'en-tête (ligne 1), les lignes vides et les commentaires
                if line_num == 1:
                    continue
                if not raw_line or raw_line.startswith("#"):
                    continue

                # Parser la ligne avec csv.reader sur une liste de 1 élément
                row_fields = list(csv.reader([line]))[0]

                # Validation des règles 1 à 11
                error_code = validate_row(row_fields, airports)
                if error_code is not None:
                    errors.append(f"{base_name}:{line_num}: {error_code} | {line.rstrip('\r\n')}")
                    continue

                # Règle 12 : DUPLICATE_FLIGHT
                record = to_record(row_fields)
                flight_key = (record["flight_id"], record["departure_datetime"])
                if flight_key in seen_flights:
                    errors.append(f"{base_name}:{line_num}: DUPLICATE_FLIGHT | {line.rstrip('\r\n')}")
                    continue

                seen_flights.add(flight_key)
                records.append(record)

    return records, errors