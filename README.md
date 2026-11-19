# Exercise: Shuttle Schedule API

Exercise code for the lesson **Exercise: Shuttle Schedule API** in the Python Web APIs course on [ask-codey.com](https://www.ask-codey.com).

The campus shuttle's API already answers riders (every route, and one route with its stops) and signs drivers in. Before it goes live for real riders, it needs what a team would ask for: settings checked when it starts, a log line for every request with secrets kept out, migrations that run as it starts, and a health check a host can call. You'll build all of them, and tests check each one.

## What's here

- `settings.py`: the `Settings` class and `load_settings()`. For you to finish: right now every setting has a default, the JWT secret included, and `.env` isn't read. The comment at its top describes the four settings and the exact message for a missing one.
- `logs.py`: `HideSecrets`, the filter that keeps passwords and tokens out of every log line, for you to finish, and `setup_logging(level)`, ready. The comment at its top lists exactly what the filter hides.
- `main.py`: the app, its routers, `problem()` and the error handlers, ready. The lifespan, the request-logging middleware and `GET /health` are for you to write. The comment at its top describes each one, with its exact log lines and answers.
- `database.py`: `open_db(path)`, `migrate(conn)` and `get_db()`, which opens `settings.database_path` for every request. Ready to use.
- `migrations/`: the three numbered scripts: the routes, their stops, and the drivers (one demo driver, `ana`, whose made-up password is `correct-horse-staple`). Ready to use.
- `shuttle_data.py`: the data module, with every SQL statement the API runs. Ready to use.
- `routers/routes.py` and `routers/auth.py`: `GET /routes`, `GET /routes/{route_id}` and the drivers' sign-in, `POST /auth/token`. Ready to use.
- `.env.example`: the four settings, with made-up values for your own computer. Copy it to `.env` (below).
- `tests/test_shuttle.py`: the tests, 19 in all. You don't need to change this file.
- `requirements.txt`: the packages the app and the tests need (FastAPI, pydantic-settings, pwdlib, PyJWT and pytest), at exact versions. Ready to use.
- `pytest.ini`: tells pytest where the tests are and where to find `main.py`. Ready to use.
- `.gitignore`: tells Git to leave out the virtual environment, the files Python and pytest make as they run, `.env` and the database file. Ready to use.

## Before you start

The app and the tests need their packages in a virtual environment: a private set of packages for this folder only. In VS Code's terminal, in this folder, run these three commands.

On Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

On a Mac (zsh):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- The first command makes the virtual environment, in a folder named `.venv`.
- The second turns it on for this terminal: the prompt starts with `(.venv)` from then on.
- The third installs the packages `requirements.txt` lists into it. It takes a minute: FastAPI brings several packages with it.

*Virtual Environments and pip* explains all three. The `.venv` folder is in `.gitignore`, so Git leaves it out: these commands make it again on any computer.

If PowerShell answers that running scripts is disabled on this system, run this once, then run the second command again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Each new terminal starts with the virtual environment off. If the prompt doesn't start with `(.venv)`, run the second command again. (VS Code often turns it on for you.)

Then copy `.env.example` to `.env`, the file the settings read on your own computer. On Windows (PowerShell):

```powershell
Copy-Item .env.example .env
```

On a Mac (zsh):

```bash
cp .env.example .env
```

`.env` is in `.gitignore`, so it never reaches GitHub. Change its `JWT_SECRET` to a long made-up value of your own.

## Run it

```bash
fastapi dev main.py
```

Then open `http://127.0.0.1:8000/docs` in your browser. Click a route, then **Try it out** and **Execute**, to send it a real request. `POST /auth/token` signs in as `ana`, with the password `correct-horse-staple`. The app restarts each time you save a file. Stop it with **Ctrl+C**.

Watch the terminal: once your work is done, it shows `Shuttle API started: ran migrations [1, 2, 3]` the first time, a line such as `GET /routes 200 3.1ms` for every request, and `Shuttle API stopped` when you press Ctrl+C. Rename `.env` for a moment, and the app stops at once with a message naming the missing settings.

## Check your work

```bash
pytest
```

No server needs to be running: the tests hand each request straight to the app. They set the four settings themselves, with a throwaway database file, so your `.env` and `shuttle.db` aren't touched. At first all 19 tests fail: that is expected. Each part you finish turns its tests green: tests 1 to 6 check `settings.py`, 7 to 9 the filter, 10 to 13 the request lines, 14 to 17 the lifespan, and 18 and 19 the health route. A failing test's message says what it expected and what came back, for example *GET /routes should log one line like 'GET /routes 200 3.1ms' from main.py's logger, but main.py's request lines were [].*

## The rules

- Write the settings in `settings.py`, the filter in `logs.py`, and the lifespan, the middleware and `GET /health` in `main.py`. Don't change the other files or the tests.
- `DATABASE_PATH` and `JWT_SECRET` have no default. `LOG_LEVEL` defaults to `"INFO"` and `TOKEN_MINUTES` to `60`, a whole number. The settings are read from the environment and from `.env`, and the environment wins.
- `load_settings()` stops the app with `sys.exit` and the exact message at the top of `settings.py`, one line per problem, never with a traceback.
- Log with `main.py`'s own logger, `logging.getLogger(__name__)`, never `print`. The request line is `"%s %s %d %.1fms"`: the method, `request.url.path` (never the whole address, which can carry a token), the status code, and the time in milliseconds.
- Never log a password, a token or the JWT secret.
- The lifespan migrates with `open_db` and `migrate` from `database.py`, closes its connection, and logs the two lines at the top of `main.py`, exactly.
- `GET /health` takes its connection from `Depends(get_db, scope="function")`, counts the `routes` table's rows, and answers `{"status": "ok"}`, or a 503 through `problem()` with the detail `The database isn't answering.` and an ERROR line that starts `Health check failed:`. Its body never holds the database's own error message.

## Tips

- Start in `settings.py`, the way *Settings Checked at Startup* does: take the defaults off the two required settings, add `model_config = SettingsConfigDict(env_file=".env")`, then the `try` and `except ValidationError` in `load_settings`.
- For the filter, the Do It in *Logging an API* hides `password=` and `token=`. The word after `Bearer` needs one more idea: remember, as you go through the words, whether the last word was `Bearer`.
- The middleware, the lifespan and the health route are in *Logging an API* and *Startup, Shutdown and a Health Check*. Use the log lines this exercise asks for, which differ from the lessons' a little.
- The middleware and the lifespan are written `async def`, with `await call_next(request)` in the middleware, as the lessons show.
- Tests 14 to 17 start the app with `with TestClient(app):`, which runs your lifespan. The others don't, so they never run it.

## Hand it in

When it works, push your solution to a public repo of your own on GitHub, then paste that repo's address into **Submit your exercise** on the lesson page at [ask-codey.com](https://www.ask-codey.com). That's what completes the lesson. The lesson page shows the Git commands, step by step.
