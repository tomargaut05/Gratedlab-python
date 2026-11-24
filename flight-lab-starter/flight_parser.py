import argparse
import datetime
import json
import logging
import os
import sys

from validator import load_airports
from csv_loader import parse_files
from query import run_queries

STUDENT_ID = "260ADB185"
FIRST_NAME = "Tom"
LAST_NAME = "Argaut"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Flight Schedule Parser and Query Tool", add_help=True)
    parser.add_argument("-i", help="Parse a single CSV file.")
    parser.add_argument("-d", help="Parse every .csv file in the folder.")
    parser.add_argument("-j", help="Load an existing JSON database.")
    parser.add_argument("-a", help="Airport list file.")
    parser.add_argument("-o", default="db.json", help="Output path for JSON database.")
    parser.add_argument("-q", help="Run queries from JSON file.")
    parser.add_argument("-r", default=".", help="Folder for query response file.")

    # Validation de l'utilisation des arguments
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        return 2

    sources = [s for s in (args.i, args.d, args.j) if s is not None]
    if len(sources) != 1:
        sys.stderr.write("Error: Exactly one data source (-i, -d, or -j) is required.\n")
        return 2

    if (args.i or args.d) and not args.a:
        sys.stderr.write("Error: -a airport file is required with -i or -d.\n")
        return 2

    if args.j and args.o != "db.json" and "-o" in (argv or sys.argv[1:]):
        sys.stderr.write("Error: -o cannot be used with -j.\n")
        return 2

    db: list[dict] = []
    logger = logging.getLogger("flight_parser")

    # Traitement des sources
    if args.j:
        if not os.path.isfile(args.j):
            sys.stderr.write("Error: JSON database file does not exist.\n")
            return 1
        try:
            with open(args.j, mode="r", encoding="utf-8") as f:
                db = json.load(f)
            if not isinstance(db, list):
                sys.stderr.write("Error: JSON database must be an array.\n")
                return 1
        except Exception:
            sys.stderr.write("Error: Failed to read JSON database file.\n")
            return 1
    else:
        if not os.path.isfile(args.a):
            sys.stderr.write("Error: Airport list file does not exist.\n")
            return 1

        try:
            airports = load_airports(args.a)
        except Exception:
            sys.stderr.write("Error: Could not read airport list file.\n")
            return 1

        csv_paths = []
        if args.i:
            if not os.path.isfile(args.i):
                sys.stderr.write("Error: CSV file does not exist.\n")
                return 1
            csv_paths.append(args.i)
        elif args.d:
            if not os.path.isdir(args.d):
                sys.stderr.write("Error: Folder does not exist.\n")
                return 1
            files = sorted([f for f in os.listdir(args.d) if f.endswith(".csv")])
            if not files:
                sys.stderr.write("Error: No .csv files found in folder.\n")
                return 1
            csv_paths = [os.path.join(args.d, f) for f in files]

        log_folder = os.path.dirname(args.o) or "."
        log_path = os.path.join(log_folder, "errors.log")

        # Configuration propre du logger (avec cleanup garanti)
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
        handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        ))
        logger.addHandler(handler)

        try:
            db, errors = parse_files(csv_paths, airports)
            for err in errors:
                logger.warning(err)
            
            with open(args.o, mode="w", encoding="utf-8") as f:
                json.dump(db, f, indent=2)
        except Exception as e:
            sys.stderr.write(f"Error: {e}\n")
            return 1
        finally:
            logger.removeHandler(handler)
            handler.close()

    # Traitement des requêtes (-q)
    if args.q:
        if not os.path.isfile(args.q):
            sys.stderr.write("Error: Query file does not exist.\n")
            return 1
        try:
            with open(args.q, mode="r", encoding="utf-8") as f:
                queries_data = json.load(f)
            if not isinstance(queries_data, (dict, list)):
                sys.stderr.write("Error: Query JSON must be an object or an array.\n")
                return 1
        except Exception:
            sys.stderr.write("Error: Failed to read query JSON file.\n")
            return 1

        responses = run_queries(db, queries_data)

        now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        res_filename = f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{now_str}.json"
        res_path = os.path.join(args.r, res_filename)

        try:
            with open(res_path, mode="w", encoding="utf-8") as f:
                json.dump(responses, f, indent=2)
        except Exception:
            sys.stderr.write("Error: Could not write response file.\n")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())