# database/connection.py - Database connection and configuration
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # dotenv is optional in testing environments
    load_dotenv = None
from contextlib import contextmanager

# Database configuration with fallback for tests
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///local.db')

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before use
    echo=os.getenv('SQL_ECHO', 'False').lower() == 'true'  # Set to True for SQL debugging
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

@contextmanager
def get_db_session():
    """Context manager for database sessions"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def init_database():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)