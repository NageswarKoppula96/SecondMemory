# SecondMemory

SecondMemory is a personal, single-user Telegram AI assistant for long-term memories, tasks, and future reminders. It uses natural-language interaction, Gemini, LangChain agent/tool calling, SQLAlchemy, SQLite, and APScheduler.

## Technology

- Python 3.12 or newer (the current development environment uses Python 3.14.x)
- FastAPI and Uvicorn for the HTTP application
- `python-telegram-bot` for Telegram polling
- LangChain and `langchain-google-genai` for the Gemini agent and tools
- SQLAlchemy with SQLite for persistence
- APScheduler for reminder execution
- Pydantic Settings and `python-dotenv` for configuration
- pytest and pytest-asyncio for tests

The dependency source of truth is `requirements.txt`. It installs the project from `pyproject.toml` in editable mode and includes the test dependencies.

## First-Time Setup After Cloning

These instructions assume Windows PowerShell and a Python installation available through the Windows Python launcher.

### 1. Clone the repository

```powershell
git clone <repository-url>
Set-Location SecondMemory
```

### 2. Verify Python

```powershell
py --version
py --list
py -3.14 --version
```

Python 3.12 or newer is required. Use `py -3.14` explicitly when creating the environment if that version is installed.

### 3. Create and activate the virtual environment

```powershell
py -3.14 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.venv\Scripts\Activate.ps1
```

The execution-policy command affects only the current PowerShell process. It does not permanently change the machine's policy. It is only needed when PowerShell blocks `Activate.ps1`.

If you do not want to activate the environment, use `.venv\Scripts\python.exe` for project commands.

### 4. Install dependencies

With the environment activated:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Do not install dependencies globally. Without activation, use:

```powershell
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 5. Create `.env`

`.env` is intentionally excluded from GitHub because it contains secrets. `.env.example` is the committed configuration template.

```powershell
Copy-Item .env.example .env
```

Open `.env` and configure these values:

| Variable | Meaning |
| --- | --- |
| `TELEGRAM_BOT_TOKEN` | Token obtained from Telegram BotFather. Never commit it. |
| `TELEGRAM_ALLOWED_USER_ID` | Numeric Telegram user ID allowed to use the bot. |
| `LLM_PROVIDER` | Use `gemini` for the current implementation. |
| `LLM_API_KEY` | Gemini API key. Never commit it. |
| `LLM_MODEL` | Gemini model name. Settings default to `gemini-2.5-flash`; verify your `.env` value. |
| `DATABASE_URL` | SQLite location, normally `sqlite:///./data/assistant.db`. |
| `TIMEZONE` | Time zone used by reminders; current value is `Asia/Kolkata`. |
| `TELEGRAM_MODE` | Telegram mode; current development mode is `polling`. |

The committed template currently contains these non-secret defaults:

```text
LLM_PROVIDER=gemini
LLM_MODEL=gemini-3.5-flash
DATABASE_URL=sqlite:///./data/assistant.db
TIMEZONE=Asia/Kolkata
TELEGRAM_MODE=polling
```

The template currently specifies `gemini-3.5-flash`, while the application settings default to `gemini-2.5-flash`. Use a model name supported by your Gemini account and provider package.

### 6. Initialize SQLite

SQLite is intentionally used because this is a personal application with a small amount of data. The initialization command creates the `data` directory, database file, and required tables. Do not manually create `assistant.db`.

```powershell
python -m app.database.init_db
```

Without activation:

```powershell
.venv\Scripts\python.exe -m app.database.init_db
```

## Run Tests

Run tests before starting the application:

```powershell
pytest
```

Without activation:

```powershell
.venv\Scripts\python.exe -m pytest
```

## Running the Application

Telegram polling and the FastAPI HTTP server are separate entry points.

```powershell
python -m app.telegram
```

This is the normal Telegram development command. It initializes SQLite, starts APScheduler, restores active reminders, and starts polling.

```powershell
python -m app.main
```

This starts the FastAPI HTTP server only; it does not start Telegram polling. The health endpoint is `http://localhost:8000/health` and returns `{"status":"ok"}`.

## First Run

1. Activate `.venv`, or use `.venv\Scripts\python.exe` for every command.
2. Confirm `.env` exists and contains valid Telegram and Gemini credentials.
3. Initialize SQLite: `python -m app.database.init_db`.
4. Run tests: `pytest`.
5. Start the bot: `python -m app.telegram`.
6. Open Telegram and send `/start`.
7. Save a memory: `Remember that my production application uses Java 21.`
8. Retrieve it: `What Java version does my production application use?`
9. Send `/memories`.
10. Ask the assistant to create, list, and complete a task.
11. Ask it to create a reminder a few minutes in the future and verify that it fires.

The bot also supports `/help`, `/tasks`, and `/reminders`. Only the numeric user ID configured in `TELEGRAM_ALLOWED_USER_ID` is authorized.

## Running the Application After the Initial Setup

After dependencies, `.env`, and SQLite have been set up, normal startup is:

```powershell
Set-Location <path-to-SecondMemory>
.venv\Scripts\Activate.ps1
python -m app.telegram
```

Without activation:

```powershell
.venv\Scripts\python.exe -m app.telegram
```

Normally, do not recreate `.venv`, reinstall Python or dependencies, recreate `.env`, manually recreate SQLite, or recreate tables on every run. Repeat setup only after a change or deletion.

## When to Reinstall Dependencies

Reinstall after a new machine, fresh clone, changes to `pyproject.toml` or `requirements.txt`, removed packages, or deletion of `.venv`:

```powershell
python -m pip install -r requirements.txt
```

## When to Reinitialize SQLite

`python -m app.database.init_db` uses SQLAlchemy `create_all` and is safe when the database already exists; existing data is preserved. It is not needed on every startup.

`data/assistant.db` contains personal memories, tasks, and reminders. Do not delete it unless you intentionally want to erase that data. Deleting it loses stored data unless a backup exists.

## Files Intentionally Excluded from Git

These local, generated, secret, or personal files should not be committed:

```text
.env
.venv/
__pycache__/
*.pyc
data/
*.db
```

`.env.example` is committed as the configuration template. A fresh clone intentionally does not contain `.env`, `.venv`, or `data/assistant.db`.

| Item | Recreate with |
| --- | --- |
| `.env` | `Copy-Item .env.example .env`, then fill in secrets |
| `.venv` | `py -3.14 -m venv .venv` |
| `data/assistant.db` | `python -m app.database.init_db` |

## Verify a Fresh Clone

```powershell
git clone <repository-url>
Set-Location SecondMemory
py --version
py -3.14 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
# Configure .env before continuing.
python -m app.database.init_db
pytest
python -m app.telegram
```

In Telegram, send `/start` and verify that the bot responds, memories can be saved and retrieved, tasks can be created/listed/completed, a reminder can be created and fired, and a one-time reminder is removed after firing.

## Troubleshooting

### Python command not found

If `python --version` fails but `py --version` works, use `py -3.14` to create the environment and `.venv\Scripts\python.exe` to run commands. Windows may have Python installed through the launcher without `python` being globally available.

### PowerShell execution policy

If activation is blocked:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.venv\Scripts\Activate.ps1
```

### Telegram `InvalidToken`

`TELEGRAM_BOT_TOKEN` must contain the actual BotFather token. Never expose it in GitHub. If it was committed or shared, revoke it through BotFather and create a replacement.

### Telegram bot receives no response

Check that the bot process is running, `/start` was sent, `TELEGRAM_ALLOWED_USER_ID` matches your numeric Telegram user ID, `.env` is in the project directory, and Telegram polling is running.

### Database not found

Run `python -m app.database.init_db` from the project directory and confirm that `DATABASE_URL` points to `sqlite:///./data/assistant.db` or another intended location.

### Dependency errors

Confirm `.venv` is active, then run `python -m pip install -r requirements.txt` again. The non-activated equivalent is `.venv\Scripts\python.exe -m pip install -r requirements.txt`.

## Architecture

```text
Telegram
	↓
Telegram Handler
	↓
AssistantAgent
	↓
Gemini
	↓
LangChain agent and tools
	↓
Service Layer
	↓
Repository Layer
	↓
SQLite
```

- Telegram handlers authorize the configured user, process commands, and forward natural-language messages.
- `AssistantAgent` creates the LangChain agent with `langchain-google-genai` and invokes tools for data operations.
- Services contain memory, task, and reminder business operations.
- Repositories read and write SQLAlchemy models.
- SQLite stores application data on disk.

The current code uses LangChain's `create_agent` runtime; there is no direct `langgraph` dependency listed in the repository configuration.

Reminder execution follows:

```text
Reminder Service
	↓
SQLite
	↓
APScheduler
	↓
Telegram notification
	↓
One-time reminder cleanup
```

At startup, active reminders are restored. After successful delivery, one-time reminders are deleted; recurring reminders are advanced to their next occurrence.

## Security

Never commit `.env`, Gemini API keys, Telegram bot tokens, personal credentials, or the personal SQLite database. Use `.env.example` for configuration templates. If a secret is accidentally committed, rotate or revoke it immediately and remove it from repository history as appropriate.

## Docker

Docker is optional for local Windows development. The provided compose configuration runs the FastAPI/Uvicorn server and mounts `./data` so SQLite survives container restarts:

```powershell
Copy-Item .env.example .env
# Configure .env first.
docker compose up --build
```

This compose command does not start Telegram polling because the Dockerfile entry point is `uvicorn app.main:app`. Run `python -m app.telegram` in the configured development environment when Telegram polling is required.

## Quick Start

For a clone where Python is already installed:

```powershell
Set-Location SecondMemory
py -3.14 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
# Configure .env.
python -m app.database.init_db
pytest
python -m app.telegram
```