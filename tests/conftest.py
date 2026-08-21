import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.database import models  # noqa: F401


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as value:
        yield value
