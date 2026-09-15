import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

# SQLite is used for this project: zero-config, fast for a few thousand leads,
# and easy for a reviewer to run locally with no external services.
# For production at scale (100k+ leads, concurrent writers), swap this
# connection string for a managed Postgres instance -- the SQLAlchemy
# models below would not need to change.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./leads.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()