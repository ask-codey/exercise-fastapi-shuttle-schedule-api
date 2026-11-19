"""The shuttle API's settings, for you to finish: read once, as the app starts, and checked before it serves anything.

Right now every setting has a default, the JWT secret included, and .env isn't read, so a host that forgets a
setting starts anyway, with a secret anyone can read here. Make the class and load_settings match this description.

The four settings, each read from the environment variable with its name in capitals, or from the .env file in this
folder (a real environment variable wins over the same name in .env):

  DATABASE_PATH   the SQLite file, such as shuttle.db                  text, required: no default
  JWT_SECRET      the secret that signs the drivers' sign-in tokens    text, required: no default
  LOG_LEVEL       how much is logged: DEBUG, INFO, WARNING or ERROR    text, default "INFO"
  TOKEN_MINUTES   how long a sign-in token lasts, in minutes           a whole number, default 60

load_settings() makes the Settings object. When a setting is missing or can't be read, it stops the app with
sys.exit and this message, one line per problem, each line two spaces, the setting's name in capitals, a colon and
Pydantic's message:

  The shuttle API can't start. Fix these settings in the environment or in .env:
    DATABASE_PATH: Field required
    JWT_SECRET: Field required
    TOKEN_MINUTES: Input should be a valid integer, unable to parse string as an integer

The last line makes the one settings object every other file imports: from settings import settings
"""
# These imports are everything the finished file needs.
import sys

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Make DATABASE_PATH and JWT_SECRET required, and read .env too (the description above says how).
    database_path: str = "shuttle.db"
    jwt_secret: str = "change-me"
    log_level: str = "INFO"
    token_minutes: int = 60


def load_settings():
    # Stop the app with the message described above when Settings() raises a ValidationError.
    return Settings()


settings = load_settings()
