from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DB_URL

if DB_URL in ("sqlite://", "sqlite:///:memory:"):
    # In memory SQLite gives every thread its own empty db, so share one connection between them
    engine = create_engine(DB_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
else:
    engine = create_engine(DB_URL)
LocalSession = sessionmaker(bind=engine)
Base = declarative_base()
