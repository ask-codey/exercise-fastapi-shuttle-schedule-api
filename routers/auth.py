"""Sign-in for the shuttle's drivers, who report delays. Ready to use.

  POST /auth/token    The sign-in form (username and password, as the docs page's Authorize button sends them).
                      200, {"access_token": "<a JWT>", "token_type": "bearer"}, when the password is right: the
                      token is signed with settings.jwt_secret and lasts settings.token_minutes minutes.
                      401, "Wrong username or password.", when it isn't.

The demo driver is ana, whose made-up password is correct-horse-staple. The route logs who signed in, never a
password or a token.
"""
import logging
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pwdlib import PasswordHash

import shuttle_data
from database import get_db
from settings import settings

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)
password_hash = PasswordHash.recommended()


@router.post("/token")
def sign_in(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    conn: sqlite3.Connection = Depends(get_db, scope="function"),
):
    driver = shuttle_data.find_driver(conn, form.username)
    if driver is None or not password_hash.verify(form.password, driver["password_hash"]):
        logger.info("Sign-in refused for %s", form.username)
        raise HTTPException(
            status_code=401, detail="Wrong username or password.", headers={"WWW-Authenticate": "Bearer"}
        )
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.token_minutes)
    token = jwt.encode({"sub": driver["username"], "exp": expires}, settings.jwt_secret, algorithm="HS256")
    logger.info("Signed in: %s", driver["username"])
    return {"access_token": token, "token_type": "bearer"}
