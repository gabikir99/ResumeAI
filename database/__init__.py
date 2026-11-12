# database/__init__.py
"""
Database package for the AI Resume Assistant
Provides PostgreSQL integration with SQLAlchemy
Simplified structure for basic user management
"""

from .connection import get_db_session, init_database, engine, Base
from .models import User, UserProfile, ChatSession, ChatMessage, JobApplication
from .service import DatabaseService

# Initialize the database service
db_service = DatabaseService()

# Helper functions for common operations
def create_account(name: str, email: str, password: str, confirm_password: str = None):
    """Helper function to create a new user account"""
    return db_service.create_user(name, email, password, confirm_password)

def login(email: str, password: str):
    """Helper function to authenticate user login"""
    return db_service.login_user(email, password)

def check_email_exists(email: str):
    """Helper function to check if email is already registered"""
    return db_service.check_email_exists(email)

__all__ = [
    # Core database components
    'get_db_session',
    'init_database', 
    'engine',
    'Base',
    
    # Models
    'User',
    'UserProfile', 
    'ChatSession',
    'ChatMessage',
    'JobApplication',
    
    # Service
    'DatabaseService',
    'db_service',
    
    # Helper functions for the UI
    'create_account',
    'login',
    'check_email_exists'
]