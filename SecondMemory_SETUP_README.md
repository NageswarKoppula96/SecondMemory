# SecondMemory

SecondMemory is a personal, single-user Telegram AI assistant for long-term memories, tasks, and future reminders.

## Technology

- Python 3.14.x (recommended/current development version)
- FastAPI and Uvicorn
- `python-telegram-bot`
- LangChain and `langchain-google-genai`
- Google Gemini (`gemini-2.5-flash`)
- SQLAlchemy
- SQLite
- APScheduler
- Pydantic Settings / python-dotenv
- pytest / pytest-asyncio

The project's dependency source of truth is `requirements.txt`, which installs the project and its test dependencies.

---

## First-Time Setup After Cloning

These instructions assume Windows PowerShell and Python installed through the Windows Python launcher.

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

Python 3.14.x is recommended for this project.

### 3. Create the virtual environment

```powershell
py -3.14 -m venv .venv
```

### 4. Activate the virtual environment

If PowerShell allows activation:

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell reports that script execution is disabled, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Then:

```powershell
.venv\Scripts\Activate.ps1
```

The execution-policy change applies only to the current PowerShell session.

If you do not want to activate the environment, use `.venv\Scripts\python.exe` for project commands.

### 5. Install dependencies

With `.venv` activated:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Without activation:

```powershell
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Do not install project dependencies globally.

---

## Environment Configuration

`.env` is intentionally excluded from GitHub because it contains secrets.

Create it from the committed template:

```powershell
Copy-Item .env.example .env
```

Open `.env` and configure:

```env
TELEGRAM_BOT_TOKEN=
TELEGRAM_ALLOWED_USER_ID=

LLM_PROVIDER=gemini
LLM_API_KEY=
LLM_MODEL=gemini-2.5-flash

DATABASE_URL=sqlite:///./data/assistant.db

TIMEZONE=Asia/Kolkata

TELEGRAM_MODE=polling
```

### Environment variables

| Variable | Purpose |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Telegram BotFather token. Never commit it. |
| `TELEGRAM_ALLOWED_USER_ID` | Numeric Telegram user ID authorized to use the bot. |
| `LLM_PROVIDER` | Current provider: `gemini`. |
| `LLM_API_KEY` | Gemini API key. Never commit it. |
| `LLM_MODEL` | Gemini model used by the application: `gemini-2.5-flash`. |
| `DATABASE_URL` | SQLite database location. |
| `TIMEZONE` | Reminder timezone. Current value: `Asia/Kolkata`. |
| `TELEGRAM_MODE` | Telegram mode. Current development mode: `polling`. |

Never put real secrets in `.env.example`, README files, source code, or Git commits.

---

## Database Setup

SecondMemory uses SQLite because it is a personal, single-user application with a small amount of data.

The runtime database is:

```text
data/assistant.db
```

Initialize it with:

```powershell
python -m app.database.init_db
```

Without an activated environment:

```powershell
.venv\Scripts\python.exe -m app.database.init_db
```

This creates the `data` directory, SQLite database, and required tables.

Do not manually create `assistant.db`.

Do not delete `data/assistant.db` unless you intentionally want to erase stored memories, tasks, and reminders.

---

## Run Tests

Run:

```powershell
pytest
```

Without activation:

```powershell
.venv\Scripts\python.exe -m pytest
```

Run the tests before starting the application after a fresh clone.

---

## Run the Telegram Bot

The Telegram bot is the normal application entry point:

```powershell
python -m app.telegram
```

Without activation:

```powershell
.venv\Scripts\python.exe -m app.telegram
```

This starts Telegram polling and the reminder scheduler.

Then open the bot in Telegram and send:

```text
/start
```

### FastAPI server

The FastAPI application is a separate entry point:

```powershell
python -m app.main
```

This starts Uvicorn on:

```text
http://localhost:8000
```

Health endpoint:

```text
http://localhost:8000/health
```

It does **not** start Telegram polling.

---

## First Run Verification

After starting:

```powershell
python -m app.telegram
```

test the following through Telegram.

### 1. Start

```text
/start
```

### 2. Save a memory

```text
Remember that my production application uses Java 21.
```

### 3. Retrieve the memory

```text
What Java version does my production application use?
```

### 4. List memories

```text
/memories
```

### 5. Create a task

Example:

```text
Create a task to review my project README.
```

### 6. List tasks

```text
/tasks
```

### 7. Complete a task

Ask the assistant to complete the task by its ID.

### 8. Create a reminder

Create a reminder a few minutes in the future for testing.

Example:

```text
Remind me in 5 minutes to check SecondMemory.
```

Verify that:

- The Telegram notification is received.
- The one-time reminder is removed after successful delivery.

### 9. List reminders

```text
/reminders
```

The bot also supports:

```text
/help
/tasks
/memories
/reminders
```

Only the numeric Telegram user ID configured in `TELEGRAM_ALLOWED_USER_ID` is authorized.

---

## Subsequent Runs

After the initial setup is complete, you do not need to recreate the environment or reinstall dependencies every time.

Open PowerShell and run:

```powershell
Set-Location <path-to-SecondMemory>
.venv\Scripts\Activate.ps1
python -m app.telegram
```

Or without activation:

```powershell
Set-Location <path-to-SecondMemory>
.venv\Scripts\python.exe -m app.telegram
```

Normally, do **not** repeat:

- Python installation
- `.venv` creation
- dependency installation
- `.env` creation
- SQLite initialization

unless the environment was deleted, dependencies changed, or you are setting up another machine.

---

## When to Reinstall Dependencies

Reinstall dependencies when:

- Setting up a fresh clone
- Setting up a new machine
- `requirements.txt` changes
- `pyproject.toml` changes
- `.venv` was deleted
- A required package was removed

Run:

```powershell
python -m pip install -r requirements.txt
```

---

## When to Reinitialize SQLite

The database initialization command uses SQLAlchemy `create_all` and can safely be run when the database already exists.

However, it is not necessary on every application startup.

The database contains personal data:

```text
data/assistant.db
```

Deleting this file deletes the stored memories, tasks, and reminders unless you have a backup.

---

## Git and Files Excluded from GitHub

The following should remain local and should not be committed:

```text
.env
.venv/
__pycache__/
*.pyc
data/
*.db
```

This is intentional.

A fresh Git clone will contain the source code and configuration template, but not:

- `.env`
- `.venv`
- `data/assistant.db`

They are recreated locally.

| Local item | Recreate with |
|---|---|
| `.env` | `Copy-Item .env.example .env`, then configure secrets |
| `.venv` | `py -3.14 -m venv .venv` |
| `data/assistant.db` | `python -m app.database.init_db` |

---

## Fresh Clone Verification

A complete fresh-clone setup is:

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

Then open Telegram and send:

```text
/start
```

Verify:

- Bot responds
- Memories can be saved
- Memories can be retrieved
- `/memories` works
- Tasks can be created, listed, and completed
- Reminders can be created
- Reminders are delivered
- One-time reminders are removed after firing

---

## Troubleshooting

### `python` command not found

If:

```powershell
python --version
```

does not work but:

```powershell
py --version
```

does, use:

```powershell
py -3.14
```

to create the virtual environment.

After creation, you can always use:

```powershell
.venv\Scripts\python.exe
```

### PowerShell activation blocked

Run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Then:

```powershell
.venv\Scripts\Activate.ps1
```

### Telegram `InvalidToken`

Check that `TELEGRAM_BOT_TOKEN` contains the actual token obtained from Telegram BotFather.

Never commit the token.

If a token was accidentally committed or exposed, revoke it through BotFather and create a replacement.

### Telegram bot receives no response

Check:

1. `python -m app.telegram` is still running.
2. `/start` was sent.
3. `TELEGRAM_ALLOWED_USER_ID` matches your numeric Telegram user ID.
4. `.env` exists in the project root.
5. `TELEGRAM_BOT_TOKEN` is correct.
6. Telegram polling is running without errors.

### Database not found

Run:

```powershell
python -m app.database.init_db
```

Then verify:

```text
data/assistant.db
```

exists.

Also verify:

```env
DATABASE_URL=sqlite:///./data/assistant.db
```

### Dependency errors

Make sure `.venv` is active and run:

```powershell
python -m pip install -r requirements.txt
```

---

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
LangChain Agent + Tools
    ↓
Service Layer
    ↓
Repository Layer
    ↓
SQLite
```

Reminder execution:

```text
Reminder Service
    ↓
SQLite
    ↓
APScheduler
    ↓
Telegram Notification
    ↓
One-time Reminder Cleanup
```

### Layer responsibilities

- **Telegram handlers** — authorize the configured user, process commands, and forward natural-language messages.
- **AssistantAgent** — creates the LangChain agent and connects Gemini with the application tools.
- **Tools** — expose memory, task, and reminder operations to the LLM.
- **Services** — contain business logic.
- **Repositories** — read and write database entities.
- **SQLite** — stores memories, tasks, and reminders.
- **APScheduler** — executes scheduled reminders.

At startup, active reminders are restored. After successful delivery, one-time reminders are removed; recurring reminders advance to their next occurrence.

---

## Security

Never commit:

- `.env`
- Gemini API keys
- Telegram bot tokens
- Personal credentials
- Personal SQLite database

Use `.env.example` as the configuration template.

If a secret is accidentally committed:

1. Revoke or rotate the secret immediately.
2. Remove the secret from the repository.
3. Remove it from Git history if necessary.

---

## Docker

Docker is optional for local Windows development.

The provided Docker configuration can be used for the FastAPI application:

```powershell
Copy-Item .env.example .env

# Configure .env first.

docker compose up --build
```

The current Docker entry point starts FastAPI/Uvicorn. It does not start Telegram polling.

For the normal Telegram development workflow, use:

```powershell
python -m app.telegram
```

---

## Quick Start

For a fresh clone on a machine with Python 3.14 installed:

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

For subsequent runs:

```powershell
Set-Location SecondMemory
.venv\Scripts\Activate.ps1
python -m app.telegram
```
