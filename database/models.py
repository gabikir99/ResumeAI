# database/models.py - Simplified User model for basic authentication
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .connection import Base
import uuid
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)  # Full Name from the UI
    email = Column(String(255), unique=True, nullable=False, index=True)  # Email Address from the UI
    password_hash = Column(String(255), nullable=False)  # Password (hashed)
    session_id = Column(String(36), nullable=True, index=True, unique=True) # storing session id for rate limit check
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    profile_picture = Column(Text, nullable=True)
    
    # Keep relationships for future features, but make them optional
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    job_applications = relationship("JobApplication", back_populates="user", cascade="all, delete-orphan")
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary (excluding sensitive data)"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'is_active': self.is_active,
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class UserProfile(Base):
    __tablename__ = 'user_profiles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    
    # Resume-related information (optional, can be filled later)
    current_role = Column(String(255))
    experience = Column(Text)
    skills = Column(JSON)  # Store as JSON array
    education = Column(Text)
    career_interests = Column(Text)
    other_info = Column(JSON)  # Store miscellaneous info as JSON
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="profile")
    
    def update_profile_data(self, info_type: str, info_value: str):
        """Update profile data based on info type"""
        if info_type == 'current_role':
            self.current_role = info_value
        elif info_type == 'experience':
            self.experience = info_value
        elif info_type == 'skills':
            # Handle skills as a list
            if self.skills is None:
                self.skills = []
            if isinstance(info_value, str):
                # Split comma-separated skills
                new_skills = [skill.strip() for skill in info_value.split(',')]
                self.skills.extend(new_skills)
            else:
                self.skills.append(info_value)
        elif info_type == 'education':
            self.education = info_value
        elif info_type == 'career_interest':
            self.career_interests = info_value
        else:
            # Store in other_info JSON field
            if self.other_info is None:
                self.other_info = {}
            self.other_info[info_type] = info_value
        
        self.updated_at = datetime.now(timezone.utc)
    
    def to_dict(self):
        """Convert profile to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'current_role': self.current_role,
            'experience': self.experience,
            'skills': self.skills,
            'education': self.education,
            'career_interests': self.career_interests,
            'other_info': self.other_info,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ChatSession(Base):
    __tablename__ = 'chat_sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Allow anonymous sessions
    title = Column(String(255))  # Optional session title
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    message_count = Column(Integer, default=0)
    first_message_time = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    
    @classmethod
    def create_session(cls, user_id=None, title=None, session_id=None):
        """Create a new chat session"""
        return cls(
            session_id=session_id or str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            last_activity=datetime.now(timezone.utc),
            message_count=0,
            first_message_time=None
        )
    
    def to_dict(self):
        """Convert session to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'title': self.title,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'message_count': self.message_count,
            'first_message_time': self.first_message_time.isoformat() if self.first_message_time else None
        }

class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey('chat_sessions.session_id'), nullable=False)
    message_type = Column(String(50), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    intent = Column(String(100))  # Classified intent
    extra_data = Column(JSON)  # Additional metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    session = relationship("ChatSession", back_populates="messages")
    
    def to_dict(self):
        """Convert message to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'message_type': self.message_type,
            'content': self.content,
            'intent': self.intent,
            'extra_data': self.extra_data,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class JobApplication(Base):
    __tablename__ = 'job_applications'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    job_url = Column(Text)
    job_description = Column(Text)
    company_name = Column(String(255))
    position_title = Column(String(255))
    tailored_resume = Column(JSON)  # Store resume data as JSON
    analysis_results = Column(JSON)  # Store analysis results as JSON
    status = Column(String(50), default='draft')  # draft, applied, interview, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="job_applications")
    
    def to_dict(self):
        """Convert job application to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'job_url': self.job_url,
            'job_description': self.job_description,
            'company_name': self.company_name,
            'position_title': self.position_title,
            'tailored_resume': self.tailored_resume,
            'analysis_results': self.analysis_results,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }