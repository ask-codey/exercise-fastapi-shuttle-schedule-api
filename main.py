"""Campus Shuttle's API: the app, its routers, its logs, its startup and shutdown, and its health check.
The routers, the logging setup, problem() and the error handlers are ready; the lifespan, the request-logging
middleware and GET /health are for you to write, where the comments below say.

Run it with:  fastapi dev main.py   (after copying .env.example to .env)
Then open http://127.0.0.1:8000/docs to try every route. Stop it with Ctrl+C.

What this file does, from top to bottom:

  Logging     setup_logging(settings.log_level) sends every line through HideSecrets (logs.py). This file's own
              logger is logging.getLogger(__name__), named "main".

  lifespan    When the app starts: opens settings.database_path with open_db, runs migrate on it, closes it, and
              logs at INFO, from this file's logger:
                  Shuttle API started: ran migrations [1, 2, 3]
              (the numbers migrate returned: [1, 2, 3] on a new database, [] on one that's up to date).
              When the app stops, it logs at INFO:  Shuttle API stopped

  Requests    A middleware logs one INFO line, from this file's logger, for every request, once it's answered:
                  GET /routes 200 3.1ms
              the method, the path without its query string (request.url.path), the status code, and how long it
              took in milliseconds with one decimal place: "%s %s %d %.1fms".

  GET /health Asks the database a real question, SELECT COUNT(*) FROM routes, through get_db (scope="function").
              200, {"status": "ok"}, when it works.
              503 in the one error shape, detail "The database isn't answering.", when it raises a sqlite3.Error,
              and an ERROR line from this file's logger that starts with:  Health check failed:

Every error answer has the API's one shape, modeled on RFC 9457's problem details:
  {"status": 404, "title": "Not Found", "detail": "There's no route moon-loop."}
"""
# These imports are everything the finished file needs.
import logging
import sqlite3
import time
from contextlib import asynccontextmanager
from http import HTTPStatus

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from database import get_db, migrate, open_db
from logs import setup_logging
from routers import auth, routes
from settings import settings

setup_logging(settings.log_level)
logger = logging.getLogger(__name__)


# Write the lifespan here, then register it: FastAPI(title="Campus Shuttle", lifespan=lifespan).


app = FastAPI(title="Campus Shuttle")
app.include_router(routes.router)
app.include_router(auth.router)


# Write the request-logging middleware here.


def problem(status, detail, problems=None, headers=None):
    body = {"status": status, "title": HTTPStatus(status).phrase, "detail": detail}
    if problems is not None:
        body["problems"] = problems
    return JSONResponse(status_code=status, content=body, headers=headers)


# Write GET /health here.


@app.exception_handler(RequestValidationError)
def validation_error(request: Request, exc: RequestValidationError):
    problems = []
    for error in exc.errors():
        problems.append({"field": error["loc"][-1], "message": error["msg"]})
    return problem(422, "The request isn't valid.", problems)


@app.exception_handler(StarletteHTTPException)
def http_error(request: Request, exc: StarletteHTTPException):
    return problem(exc.status_code, exc.detail, headers=exc.headers)


@app.exception_handler(Exception)
def server_error(request: Request, exc: Exception):
    return problem(500, "Something went wrong on our side.")
