# SecondMemory

A single-user Telegram assistant for durable memories, tasks, and reminders.

## Run locally

1. Install Python 3.12+.
2. Create an environment and install dependencies:

	`py -3 -m venv .venv`

	`\.venv\Scripts\python -m pip install -r requirements.txt`

3. Copy `.env.example` to `.env` and set `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USER_ID`, and `LLM_API_KEY`.
4. Start the API with `\.venv\Scripts\python -m app.main`.
5. Start Telegram polling in another terminal with `\.venv\Scripts\python -m app.telegram`.

`GET http://localhost:8000/health` returns `{"status":"ok"}`.

## Tests

`py -3 -m pytest`

## Docker

Copy `.env.example` to `.env`, fill in secrets, then run `docker compose up --build`. The `data` directory is mounted so SQLite survives container restarts.

The database is the source of truth. The scheduler restores active reminders at startup, removes one-time reminders after successful delivery, and advances recurring reminders.