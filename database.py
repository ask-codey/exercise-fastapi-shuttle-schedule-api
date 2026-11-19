"""The shuttle API's database: how a connection is opened, the migrations, and get_db, the dependency that gives
every request its own connection. Ready to use: you don't need to change this file."""
import sqlite3
from pathlib import Path

from settings import settings

# The numbered migration scripts: 0001_create_routes.sql, 0002_create_stops.sql, 0003_create_drivers.sql.
MIGRATIONS = Path(__file__).parent / "migrations"


def open_db(path):
    """Opens the database file at path, with rows you can read by column name and foreign keys checked.

    check_same_thread=False: FastAPI may open a request's connection in one of its threads and use it in another.
    It's safe because each request gets a connection of its own.
    """
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def migrate(conn):
    """Runs, in order, every script in migrations/ whose number is higher than the database's PRAGMA user_version,
    and sets user_version to each script's number after it runs. Returns the numbers it ran, such as [1, 2, 3], or
    [] when the database is up to date."""
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    ran = []
    for path in sorted(MIGRATIONS.glob("*.sql")):
        number = int(path.name[:4])
        if number > version:
            conn.executescript(path.read_text(encoding="utf-8"))
            # PRAGMA takes no placeholders. number is an int from our own file name, never from a request.
            conn.execute(f"PRAGMA user_version = {number}")
            conn.commit()
            ran.append(number)
    return ran


def get_db():
    """Gives each request its own connection to the file settings.database_path names: commits when the route
    finishes without an error, rolls back when it raises one, and always closes it."""
    conn = open_db(settings.database_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
