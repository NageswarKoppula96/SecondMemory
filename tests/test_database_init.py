from pathlib import Path

from sqlalchemy import inspect

from app.database.database import build_engine
from app.database.init_db import init_db


def test_init_db_creates_sqlite_file_and_all_tables(tmp_path: Path):
    database_path = tmp_path / "data" / "assistant.db"
    database_url = f"sqlite:///{database_path.as_posix()}"

    init_db(database_url)

    assert database_path.is_file()
    assert set(inspect(build_engine(database_url)).get_table_names()) == {
        "memories",
        "tasks",
        "reminders",
        "reminder_history",
    }