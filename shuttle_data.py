"""The shuttle API's data module: every SQL statement the API runs, in one place. Ready to use.

Each function takes an open connection and gives back plain Python values: a dictionary, a list of dictionaries, or
None for a row that isn't there. Every value goes into the SQL through a ? placeholder.
"""


def list_routes(conn):
    """Every route, sorted by id, each as {"id", "name", "every_minutes", "first_bus", "last_bus"}."""
    rows = conn.execute("SELECT id, name, every_minutes, first_bus, last_bus FROM routes ORDER BY id").fetchall()
    return [dict(row) for row in rows]


def get_route(conn, route_id):
    """The route with this id, with "stops": its stops' names in order. None when there's no such route."""
    row = conn.execute(
        "SELECT id, name, every_minutes, first_bus, last_bus FROM routes WHERE id = ?", (route_id,)
    ).fetchone()
    if row is None:
        return None
    route = dict(row)
    stops = conn.execute("SELECT name FROM stops WHERE route_id = ? ORDER BY position", (route_id,)).fetchall()
    route["stops"] = [stop["name"] for stop in stops]
    return route


def find_driver(conn, username):
    """The driver with this username as {"id", "username", "password_hash"}, or None."""
    row = conn.execute("SELECT id, username, password_hash FROM drivers WHERE username = ?", (username,)).fetchone()
    return None if row is None else dict(row)
