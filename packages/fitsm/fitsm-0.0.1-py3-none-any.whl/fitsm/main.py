import argparse
import yaml
from pathlib import Path
from tqdm import tqdm
from functools import partial
from fitsm.core import (
    get_files,
    instruments_name_keywords,
    instruments_definitions,
    get_definition,
    get_data,
)
from fitsm.db import db_connection, insert_file


def filter_query(table, instrument=None, date=None, filter_=None, object_=None):
    conditions = []
    if instrument:
        conditions.append(f"instrument REGEXP ?")
    if date:
        conditions.append(f"date REGEXP ?")
    if filter_:
        conditions.append(f"filter REGEXP ?")
    if object_:
        conditions.append(f"object REGEXP ?")
    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    return f"SELECT * FROM {table} {where}"


def get_query_params(instrument=None, date=None, filter_=None, object_=None):
    params = []
    if instrument:
        params.append(instrument)
    if date:
        params.append(date)
    if filter_:
        params.append(filter_)
    if object_:
        params.append(object_)
    return params


def add_regexp_to_connection(con):
    import re

    def regexp(expr, item):
        if item is None:
            return False
        return re.search(expr, str(item), re.IGNORECASE) is not None

    con.create_function("REGEXP", 2, regexp)


def index_folder(folder: str, instruments_file: str, db_file: str):
    folder_path = Path(folder)
    if not folder_path.exists():
        raise FileNotFoundError(f"Folder '{folder}' does not exist.")
    instruments_path = Path(instruments_file)
    if not instruments_path.exists():
        raise FileNotFoundError(
            f"Instruments file '{instruments_file}' does not exist."
        )
    with open(instruments_path, "r") as f:
        config = yaml.safe_load(f)
    name_keywords = instruments_name_keywords(config)
    definitions = instruments_definitions(config)
    files = list(get_files(folder, "*.f*t*"))
    get_def = partial(get_definition, keywords=name_keywords, definitions=definitions)
    con = db_connection(db_file)
    for file in tqdm(files):
        try:
            data = get_data(file, get_def)
            insert_file(con, data)
        except Exception as e:
            print(f"Error processing file {file}: {e}")
    con.commit()
    con.close()
    print(f"Database created at: {db_file}")


def show_table(table, db_path, instrument, date, filter_, object_):
    import pandas as pd

    con = db_connection(db_path)
    add_regexp_to_connection(con)
    query = filter_query(table, instrument, date, filter_, object_)
    params = get_query_params(instrument, date, filter_, object_)
    df = pd.read_sql_query(query, con, params=params)
    print(df)
    con.close()


def main():
    parser = argparse.ArgumentParser(description="FITS parser CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # index command
    index_parser = subparsers.add_parser(
        "index", help="Index FITS files into a database."
    )
    index_parser.add_argument("folder", type=str, help="Folder containing FITS files.")
    index_parser.add_argument(
        "-i",
        "--instruments",
        type=str,
        required=True,
        help="Path to instruments.yaml file.",
    )
    index_parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Path to output database file (default: fits_data.db in folder)",
    )

    # show observations
    show_obs_parser = subparsers.add_parser(
        "observations", help="Show observations from the database."
    )
    show_obs_parser.add_argument("db", type=str, help="Path to the database file.")
    show_obs_parser.add_argument("-i", "--instrument", type=str, default=None)
    show_obs_parser.add_argument("-d", "--date", type=str, default=None)
    show_obs_parser.add_argument(
        "-f", "--filter", dest="filter_", type=str, default=None
    )
    show_obs_parser.add_argument(
        "-o", "--object", dest="object_", type=str, default=None
    )

    # show files
    show_files_parser = subparsers.add_parser(
        "files", help="Show files from the database."
    )
    show_files_parser.add_argument("db", type=str, help="Path to the database file.")
    show_files_parser.add_argument("-i", "--instrument", type=str, default=None)
    show_files_parser.add_argument("-d", "--date", type=str, default=None)
    show_files_parser.add_argument(
        "-f", "--filter", dest="filter_", type=str, default=None
    )
    show_files_parser.add_argument(
        "-o", "--object", dest="object_", type=str, default=None
    )

    # query command
    query_parser = subparsers.add_parser(
        "query", help="Run a custom SQL query on the database."
    )
    query_parser.add_argument("db", type=str, help="Path to the database file.")
    query_parser.add_argument("sql", type=str, help="SQL query string to execute.")

    args = parser.parse_args()

    if args.command == "index":
        db_path = (
            args.output if args.output else str(Path(args.folder) / "fits_data.db")
        )
        index_folder(args.folder, args.instruments, db_path)
    elif args.command == "observations":
        show_table(
            "observations",
            args.db,
            args.instrument,
            args.date,
            args.filter_,
            args.object_,
        )
    elif args.command == "files":
        show_table(
            "files", args.db, args.instrument, args.date, args.filter_, args.object_
        )
    elif args.command == "query":
        import pandas as pd

        con = db_connection(args.db)
        add_regexp_to_connection(con)
        df = pd.read_sql_query(args.sql, con)
        print(df)
        con.close()


if __name__ == "__main__":
    main()
