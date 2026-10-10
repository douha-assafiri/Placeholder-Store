from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DB_URL

engine = create_engine(DB_URL)
LocalSession = sessionmaker(bind=engine)
Base = declarative_base()
