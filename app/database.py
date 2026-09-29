import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

# Load variables from .env file (DATABASE_URL, etc.)
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@localhost:3306/bankdb")

# The engine is the connection to the database
engine = create_engine(DATABASE_URL)

# SessionLocal is a factory that creates new database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Base class that all ORM models will inherit from
class Base(DeclarativeBase):
    pass


def get_db():
    """
    FastAPI dependency that provides a database session per request.
    The session is automatically closed when the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
