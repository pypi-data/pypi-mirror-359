import sqlite3
from pathlib import Path
from datetime import datetime

# Convenience
# -----------
SQL_DAYS_BETWEEN = "date >= date('{date}', '-{past:.0f} days') AND date <= date('{date}', '+{future:.0f} days')"
PWD = Path(__file__).parent


def in_value(value):
    return f"'{value}'" if isinstance(value, str) else value


def exposure_constraint(exposure=0, tolerance=1000000):
    return f"exposure between {exposure-tolerance} and {exposure+tolerance}"


def db_connection(file=None):
    if file is None:
        file = ":memory:"

    con = sqlite3.connect(file)
    cur = con.cursor()

    # check if file Table exists
    tables = list(cur.execute("SELECT name FROM sqlite_master WHERE type='table';"))
    if len(tables) == 0:
        db_creation = open(PWD / "create_fm_db.sql", "r").read()
        cur.executescript(db_creation)

    return con


from datetime import datetime
from datetime import timedelta


def in_value(value):
    return f"'{value}'" if isinstance(value, str) else value


def insert_file(con, data, update_obs=True):
    _data = data.copy()
    if _data["filter"]:
        _data["filter"] = data["filter"].replace("'", "p")

    # update observation
    if update_obs:
        _data["date"] = datetime.date(data["date"] - timedelta(hours=10))
        _data["date"] = _data["date"].strftime("%Y-%m-%d")
        unique_obs = (
            "date",
            "instrument",
            "filter",
            "object",
            "type",
            "width",
            "height",
            "exposure",
        )
        con.execute(
            f"INSERT or IGNORE INTO observations({','.join(unique_obs)}, files) VALUES ({','.join(['?'] * len(unique_obs))}, 0)",
            [_data[o] for o in unique_obs],
        )
        query = " AND ".join(
            [f"{str(key)} = {in_value(_data[key])}" for key in unique_obs]
        )
        try:
            id = con.execute(f"SELECT id FROM observations where {query}").fetchall()[
                0
            ][0]
        except:
            print(query)
        con.execute(f"UPDATE observations SET files = files + 1 WHERE id = {id}")
    else:
        id = None

    obs = [
        "date",
        "instrument",
        "filter",
        "object",
        "type",
        "width",
        "height",
        "exposure",
        "ra",
        "dec",
        "jd",
        "hash",
        "path",
    ]

    _data["date"] = data["date"].strftime("%Y-%m-%d %H:%M:%S")

    con.execute(
        f"INSERT or IGNORE INTO files({','.join(obs)}, id) VALUES ({','.join(['?'] * len(obs))}, {id})",
        [_data[o] for o in obs],
    )
