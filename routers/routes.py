"""The shuttle's routes, for riders. Ready to use.

  GET /routes              200, every route, sorted by id
  GET /routes/night-owl    200, one route with its stops in order
  GET /routes/moon-loop    404, "There's no route moon-loop."
"""
import sqlite3

from fastapi import APIRouter, Depends, HTTPException

import shuttle_data
from database import get_db

router = APIRouter(prefix="/routes", tags=["routes"])


@router.get("")
def list_routes(conn: sqlite3.Connection = Depends(get_db, scope="function")):
    return shuttle_data.list_routes(conn)


@router.get("/{route_id}")
def get_route(route_id: str, conn: sqlite3.Connection = Depends(get_db, scope="function")):
    route = shuttle_data.get_route(conn, route_id)
    if route is None:
        raise HTTPException(status_code=404, detail=f"There's no route {route_id}.")
    return route
