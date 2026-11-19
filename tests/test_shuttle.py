# Tests for the shuttle API. Run them with: pytest (in the exercise folder, with the virtual environment active).
# The settings are read when settings.py is first imported, so this file sets them first: a throwaway database file
# in a folder of its own, a made-up secret, INFO logs and 60-minute tokens. They win over your own .env, which the
# tests never change. Tests 1 to 6 check settings.py, 7 to 9 the filter in logs.py, and 10 to 19 main.py: they send
# requests with TestClient and read the log lines with pytest's caplog. A failing test says what it expected and
# what came back.
# You don't need to change this file.
import os
import tempfile

TEST_FOLDER = tempfile.mkdtemp(prefix="shuttle-tests-")
DATABASE_PATH = os.path.join(TEST_FOLDER, "shuttle_test.db")
os.environ["DATABASE_PATH"] = DATABASE_PATH
os.environ["JWT_SECRET"] = "test-secret-change-me-it-is-not-a-real-one"
os.environ["LOG_LEVEL"] = "INFO"
os.environ["TOKEN_MINUTES"] = "60"

import io  # noqa: E402
import logging  # noqa: E402
import re  # noqa: E402
import sqlite3  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from pydantic import ValidationError  # noqa: E402

from database import migrate, open_db  # noqa: E402
from logs import HideSecrets  # noqa: E402
from main import app  # noqa: E402
from settings import Settings, load_settings  # noqa: E402

# A client that doesn't run the lifespan (no with block), for the tests that bring their own database.
# raise_server_exceptions=False: a crash comes back as the 500 answer a caller would get.
client = TestClient(app, raise_server_exceptions=False)

SETTING_NAMES = ["DATABASE_PATH", "JWT_SECRET", "LOG_LEVEL", "TOKEN_MINUTES"]
START = "The shuttle API can't start. Fix these settings in the environment or in .env:"
TITLES_503 = ["Service Unavailable"]


def remove_database():
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)


@pytest.fixture
def migrated_database():
    """A new database file at DATABASE_PATH, with every migration run: the three routes and the driver ana."""
    remove_database()
    conn = open_db(DATABASE_PATH)
    migrate(conn)
    conn.close()
    yield DATABASE_PATH
    remove_database()


@pytest.fixture
def no_database():
    """No database file at all at DATABASE_PATH, as on a host's first start."""
    remove_database()
    yield DATABASE_PATH
    remove_database()


@pytest.fixture
def clean_environment(monkeypatch, tmp_path):
    """For the settings tests: none of the four settings in the environment, and an empty folder as the current
    folder, so no .env file is found unless the test writes one."""
    for name in SETTING_NAMES:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.chdir(tmp_path)
    return tmp_path


def stop_message(stop):
    """The text load_settings stopped the app with."""
    return str(stop.value.code)


def main_lines(caplog, level=logging.INFO):
    """The lines main.py's own logger wrote at this level, as text."""
    return [record.getMessage() for record in caplog.records if record.name == "main" and record.levelno == level]


def request_lines(caplog):
    """main.py's INFO lines that look like a request line: they start with a method."""
    return [line for line in main_lines(caplog) if line.split(" ")[0] in ("GET", "POST", "PUT", "PATCH", "DELETE")]


def check_request_line(caplog, method_and_path, status):
    lines = request_lines(caplog)
    pattern = "^" + re.escape(f"{method_and_path} {status} ") + r"\d+\.\dms$"
    assert len(lines) == 1 and re.match(pattern, lines[0]), (
        f"{method_and_path} should log one line like '{method_and_path} {status} 3.1ms' from main.py's logger, "
        f"but main.py's request lines were {lines!r}."
    )


def app_log(caplog):
    """Every line the app's own loggers wrote, as text. TestClient's own lines (from httpx) are left out: they show
    the whole address a test asked for, the way a browser's history would."""
    return "\n".join(record.getMessage() for record in caplog.records if not record.name.startswith("httpx"))


def written(message, *values):
    """The line HideSecrets lets through when message is logged with these values."""
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(message)s"))
    handler.addFilter(HideSecrets())
    logger = logging.getLogger("shuttle.tests")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.handlers = [handler]
    logger.info(message, *values)
    return stream.getvalue().strip()


# ---- settings.py


def test_1_settings_without_JWT_SECRET_are_refused(clean_environment, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", "shuttle.db")
    with pytest.raises(ValidationError):
        Settings()
        pytest.fail("Settings() with no JWT_SECRET anywhere should be refused, but it was made: give jwt_secret "
                    "no default.")


def test_2_settings_without_DATABASE_PATH_are_refused(clean_environment, monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "change-me")
    with pytest.raises(ValidationError):
        Settings()
        pytest.fail("Settings() with no DATABASE_PATH anywhere should be refused, but it was made: give "
                    "database_path no default.")


def test_3_settings_read_a_dot_env_file_with_TOKEN_MINUTES_45_as_the_number_45(clean_environment):
    (clean_environment / ".env").write_text(
        "DATABASE_PATH=from-env-file.db\nJWT_SECRET=change-me\nLOG_LEVEL=DEBUG\nTOKEN_MINUTES=45\n", encoding="utf-8"
    )
    try:
        found = Settings()
    except ValidationError as error:
        pytest.fail(f"Settings() should read .env, but it was refused: {error}")
    got = (found.database_path, found.jwt_secret, found.log_level, found.token_minutes)
    assert got == ("from-env-file.db", "change-me", "DEBUG", 45), (
        f"With the four settings in .env, Settings() should hold ('from-env-file.db', 'change-me', 'DEBUG', 45), "
        f"but it holds {got!r}."
    )


def test_4_a_real_environment_variable_wins_over_dot_env(clean_environment, monkeypatch):
    (clean_environment / ".env").write_text(
        "DATABASE_PATH=from-env-file.db\nJWT_SECRET=change-me\nLOG_LEVEL=DEBUG\n", encoding="utf-8"
    )
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    try:
        found = Settings()
    except ValidationError as error:
        pytest.fail(f"Settings() should read .env, but it was refused: {error}")
    got = (found.database_path, found.log_level, found.token_minutes)
    assert got == ("from-env-file.db", "WARNING", 60), (
        f"With LOG_LEVEL=DEBUG in .env and LOG_LEVEL=WARNING in the environment, Settings() should hold "
        f"('from-env-file.db', 'WARNING', 60), but it holds {got!r}."
    )


def test_5_load_settings_with_JWT_SECRET_missing_stops_with_a_message_naming_it(clean_environment, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", "shuttle.db")
    expected = START + "\n  JWT_SECRET: Field required"
    with pytest.raises(SystemExit) as stop:
        load_settings()
        pytest.fail("load_settings() with no JWT_SECRET should stop the app with sys.exit, but it returned.")
    assert stop_message(stop) == expected, (
        f"load_settings() should stop with {expected!r}, but it stopped with {stop_message(stop)!r}."
    )


def test_6_load_settings_names_every_problem_at_once(clean_environment, monkeypatch):
    monkeypatch.setenv("TOKEN_MINUTES", "sixty")
    expected = (
        START
        + "\n  DATABASE_PATH: Field required"
        + "\n  JWT_SECRET: Field required"
        + "\n  TOKEN_MINUTES: Input should be a valid integer, unable to parse string as an integer"
    )
    try:
        load_settings()
    except SystemExit as stop:
        assert str(stop.code) == expected, (
            f"load_settings() should stop with {expected!r}, but it stopped with {str(stop.code)!r}."
        )
    except ValidationError as error:
        pytest.fail(f"load_settings() should catch the ValidationError and stop with sys.exit, but it raised: {error}")
    else:
        pytest.fail("load_settings() with no DATABASE_PATH or JWT_SECRET and TOKEN_MINUTES=sixty should stop the app, "
                    "but it returned.")


# ---- logs.py: HideSecrets


def test_7_hide_secrets_writes_password_correct_horse_staple_as_password_stars():
    got = written("Sign-in form: username=%s password=%s", "ana", "correct-horse-staple")
    assert got == "Sign-in form: username=ana password=***", (
        f"The line should be written as 'Sign-in form: username=ana password=***', but it was {got!r}."
    )


def test_8_hide_secrets_writes_token_abc123_as_token_stars_and_leaves_the_rest():
    got = written("GET /routes token=%s 200", "abc123")
    assert got == "GET /routes token=*** 200", (
        f"The line should be written as 'GET /routes token=*** 200', but it was {got!r}."
    )


def test_9_hide_secrets_hides_the_word_after_Bearer():
    got = written("Header Authorization: Bearer %s from %s", "abc.def.ghi", "ana")
    assert got == "Header Authorization: Bearer *** from ana", (
        f"The line should be written as 'Header Authorization: Bearer *** from ana', but it was {got!r}."
    )


# ---- main.py: one line for every request


def test_10_get_routes_logs_GET_routes_200(migrated_database, caplog):
    caplog.set_level(logging.INFO)
    response = client.get("/routes")
    assert response.status_code == 200, f"GET /routes should answer 200, but it answered {response.status_code}."
    check_request_line(caplog, "GET /routes", 200)


def test_11_get_routes_moon_loop_logs_its_404(migrated_database, caplog):
    caplog.set_level(logging.INFO)
    client.get("/routes/moon-loop")
    check_request_line(caplog, "GET /routes/moon-loop", 404)


def test_12_a_token_in_the_query_string_never_reaches_the_log(migrated_database, caplog):
    caplog.set_level(logging.INFO)
    client.get("/routes?token=abc123")
    check_request_line(caplog, "GET /routes", 200)
    assert "abc123" not in app_log(caplog), f"The token abc123 is in the app's log:\n{app_log(caplog)}"


def test_13_signing_in_logs_the_request_but_never_the_password_or_the_token(migrated_database, caplog):
    caplog.set_level(logging.INFO)
    response = client.post("/auth/token", data={"username": "ana", "password": "correct-horse-staple"})
    assert response.status_code == 200, f"Signing in as ana should answer 200, but it answered {response.text}"
    check_request_line(caplog, "POST /auth/token", 200)
    token = response.json()["access_token"]
    assert "correct-horse-staple" not in app_log(caplog), f"Ana's password is in the app's log:\n{app_log(caplog)}"
    assert token not in app_log(caplog), f"Ana's token is in the app's log:\n{app_log(caplog)}"


# ---- main.py: the lifespan


def test_14_starting_the_app_runs_every_migration(no_database):
    with TestClient(app):
        pass
    assert os.path.exists(DATABASE_PATH), "Starting the app should make the database file, but there's no file."
    conn = sqlite3.connect(DATABASE_PATH)
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    conn.close()
    assert version == 3, f"After the app starts, PRAGMA user_version should be 3, but it's {version}."


def test_15_starting_the_app_logs_Shuttle_API_started_ran_migrations_1_2_3(no_database, caplog):
    caplog.set_level(logging.INFO)
    with TestClient(app):
        lines = main_lines(caplog)
    assert "Shuttle API started: ran migrations [1, 2, 3]" in lines, (
        f"Starting the app on a new database should log 'Shuttle API started: ran migrations [1, 2, 3]', but "
        f"main.py logged {lines!r}."
    )


def test_16_starting_it_again_runs_nothing_new(migrated_database, caplog):
    caplog.set_level(logging.INFO)
    with TestClient(app):
        lines = main_lines(caplog)
    assert "Shuttle API started: ran migrations []" in lines, (
        f"Starting the app on an up-to-date database should log 'Shuttle API started: ran migrations []', but "
        f"main.py logged {lines!r}."
    )


def test_17_stopping_the_app_logs_Shuttle_API_stopped(migrated_database, caplog):
    caplog.set_level(logging.INFO)
    with TestClient(app):
        during = list(main_lines(caplog))
    after = main_lines(caplog)
    assert "Shuttle API stopped" not in during and after[-1:] == ["Shuttle API stopped"], (
        f"'Shuttle API stopped' should be logged as the app stops, the last line, but main.py logged {after!r}."
    )


# ---- main.py: GET /health


def test_18_get_health_answers_200_status_ok(migrated_database):
    response = client.get("/health")
    assert response.status_code == 200, f"GET /health should answer 200, but it answered {response.status_code}."
    assert response.json() == {"status": "ok"}, (
        f"GET /health should answer {{'status': 'ok'}}, but it answered {response.text}"
    )


def test_19_get_health_on_an_empty_database_answers_503_and_logs_an_error(no_database, caplog):
    caplog.set_level(logging.INFO)
    response = client.get("/health")
    expected = {"status": 503, "title": "Service Unavailable", "detail": "The database isn't answering."}
    assert response.status_code == 503, (
        f"GET /health with no routes table should answer 503, but it answered {response.status_code} "
        f"with {response.text}"
    )
    assert response.json() == expected, f"GET /health should answer {expected!r}, but it answered {response.text}"
    errors = main_lines(caplog, logging.ERROR)
    assert len(errors) == 1 and errors[0].startswith("Health check failed:"), (
        f"A failed health check should log one ERROR line starting 'Health check failed:', but main.py's ERROR "
        f"lines were {errors!r}."
    )
