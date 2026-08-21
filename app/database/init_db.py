from app.config.settings import get_settings
from app.database.database import Base, build_engine
from app.database import models  # noqa: F401


def init_db(database_url: str | None = None) -> None:
    url = database_url or get_settings().database_url
    engine = build_engine(url)
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
