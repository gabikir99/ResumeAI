# database/service.py - Simplified database service layer
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from .connection import get_db_session, init_database
from .models import User, UserProfile, ChatSession, ChatMessage, JobApplication
import uuid
from datetime import datetime, timedelta

class DatabaseService:
    """Service layer for database operations"""
    
    def __init__(self):
        # Initialize database on first use
        init_database()
    
    # User Management - Simplified for the UI
    def create_user(self, name: str, email: str, password: str, confirm_password: str = None) -> Dict[str, Any]:
        """Create a new user - matching the simple UI form"""
        
        # Basic validation
        if not name or not name.strip():
            raise ValueError("Full name is required")
        
        if not email or not email.strip():
            raise ValueError("Email address is required")
        
        if not password:
            raise ValueError("Password is required")
        
        # Optional: check password confirmation
        if confirm_password is not None and password != confirm_password:
            raise ValueError("Passwords do not match")
        
        # Basic email validation
        if '@' not in email or '.' not in email.split('@')[1]:
            raise ValueError("Please enter a valid email address")
        
        with get_db_session() as session:
            # Check if user already exists
            existing_user = session.query(User).filter(User.email == email.lower().strip()).first()
            if existing_user:
                raise ValueError("An account with this email already exists")
            
            # Create user
            user = User(
                name=name.strip(),
                email=email.lower().strip()
            )
            user.set_password(password)
            session.add(user)
            session.flush()  # Get the user ID
            
            # Create empty profile for future use
            profile = UserProfile(user_id=user.id)
            session.add(profile)
            
            return {
                'success': True,
                'message': 'Account created successfully',
                'user': user.to_dict()
            }
    def assign_session_to_user(self, user_id: int, session_id: str) -> bool:
        """Assign session_id to user"""
        with get_db_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.session_id = session_id
                user.updated_at = datetime.utcnow()
            session.commit()  
            return True
        return False

    def get_user_by_session_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get user by session_id"""
        with get_db_session() as session:
            user = session.query(User).filter(User.session_id == session_id).first()
        return user.to_dict() if user else None
    
    def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user login - for future login functionality"""
        if not email or not password:
            return {
                'success': False,
                'message': 'Email and password are required'
            }
        
        with get_db_session() as session:
            user = session.query(User).filter(
                and_(
                    User.email == email.lower().strip(),
                    User.is_active == True
                )
            ).first()
            
            if user and user.check_password(password):
                return {
                    'success': True,
                    'message': 'Login successful',
                    'user': user.to_dict()
                }
            else:
                return {
                    'success': False,
                    'message': 'Invalid email or password'
                }
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        with get_db_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            return user.to_dict() if user else None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        with get_db_session() as session:
            user = session.query(User).filter(User.email == email.lower().strip()).first()
            return user.to_dict() if user else None
    
    def check_email_exists(self, email: str) -> bool:
        """Check if email is already registered"""
        with get_db_session() as session:
            user = session.query(User).filter(User.email == email.lower().strip()).first()
            return user is not None
    
    # Profile Management - Keep for future functionality
    def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user profile"""
        with get_db_session() as session:
            profile = session.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            return profile.to_dict() if profile else None
    
    def update_user_profile(self, user_id: int, info_type: str, info_value: str) -> Dict[str, Any]:
        """Update user profile based on intent classification"""
        with get_db_session() as session:
            profile = session.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            
            if not profile:
                profile = UserProfile(user_id=user_id)
                session.add(profile)
            
            profile.update_profile_data(info_type, info_value)
            return profile.to_dict()
    
    # Session Management - Keep for chat functionality
    def create_chat_session(self, user_id: Optional[int] = None) -> str:
        """Create a new chat session and return session_id"""
        with get_db_session() as session:
            chat_session = ChatSession.create_session(user_id=user_id)
            session.add(chat_session)
            session.flush()  # Ensure we get the session_id
            return chat_session.session_id
    
    def get_chat_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get chat session by ID"""
        with get_db_session() as session:
            chat_session = session.query(ChatSession).filter(
                ChatSession.session_id == session_id
            ).first()
            return chat_session.to_dict() if chat_session else None
    
    def get_user_sessions(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent chat sessions for a user"""
        with get_db_session() as session:
            sessions = session.query(ChatSession).filter(
                ChatSession.user_id == user_id
            ).order_by(desc(ChatSession.last_activity)).limit(limit).all()
            
            return [s.to_dict() for s in sessions]
    
    def update_session_activity(self, session_id: str):
        """Update last activity timestamp for session"""
        with get_db_session() as session:
            chat_session = session.query(ChatSession).filter(
                ChatSession.session_id == session_id
            ).first()
            if chat_session:
                chat_session.last_activity = datetime.utcnow()
    
    # Message Management - Keep for chat functionality
    def save_message(self, session_id: str, message_type: str, content: str, 
                    intent: Optional[str] = None, extra_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Save a chat message"""
        with get_db_session() as session:
            # Update session activity
            self.update_session_activity(session_id)
            
            message = ChatMessage(
                session_id=session_id,
                message_type=message_type,
                content=content,
                intent=intent,
                extra_data=extra_data or {}
            )
            session.add(message)
            session.flush()
            return message.to_dict()
    
    def get_session_messages(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get messages for a session"""
        with get_db_session() as session:
            messages = session.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(ChatMessage.created_at).limit(limit).all()
            
            return [m.to_dict() for m in messages]
    
    def clear_session_messages(self, session_id: str) -> bool:
        """Clear all messages for a session"""
        with get_db_session() as session:
            deleted_count = session.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).delete()
            return deleted_count > 0
    
    # Job Application Management - Keep for future functionality
    def save_job_application(self, user_id: int, job_url: Optional[str] = None,
                           job_description: Optional[str] = None, company_name: Optional[str] = None,
                           position_title: Optional[str] = None, tailored_resume: Optional[Dict] = None,
                           analysis_results: Optional[Dict] = None) -> Dict[str, Any]:
        """Save a job application"""
        with get_db_session() as session:
            job_app = JobApplication(
                user_id=user_id,
                job_url=job_url,
                job_description=job_description,
                company_name=company_name,
                position_title=position_title,
                tailored_resume=tailored_resume,
                analysis_results=analysis_results
            )
            session.add(job_app)
            session.flush()
            return job_app.to_dict()
    
    def get_user_job_applications(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get job applications for a user"""
        with get_db_session() as session:
            applications = session.query(JobApplication).filter(
                JobApplication.user_id == user_id
            ).order_by(desc(JobApplication.created_at)).limit(limit).all()
            
            return [app.to_dict() for app in applications]
    
    def update_job_application(self, application_id: int, **updates) -> Optional[Dict[str, Any]]:
        """Update a job application"""
        with get_db_session() as session:
            job_app = session.query(JobApplication).filter(
                JobApplication.id == application_id
            ).first()
            
            if not job_app:
                return None
            
            for key, value in updates.items():
                if hasattr(job_app, key):
                    setattr(job_app, key, value)
            
            job_app.updated_at = datetime.utcnow()
            return job_app.to_dict()
    
    # Utility Methods
    def cleanup_old_sessions(self, days_old: int = 7):
        """Clean up old inactive sessions"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        with get_db_session() as session:
            old_sessions = session.query(ChatSession).filter(
                ChatSession.last_activity < cutoff_date
            ).all()
            
            for old_session in old_sessions:
                session.delete(old_session)
            
            return len(old_sessions)
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user statistics"""
        with get_db_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return {}
            
            total_sessions = session.query(ChatSession).filter(
                ChatSession.user_id == user_id
            ).count()
            
            total_messages = session.query(ChatMessage).join(ChatSession).filter(
                ChatSession.user_id == user_id
            ).count()
            
            total_applications = session.query(JobApplication).filter(
                JobApplication.user_id == user_id
            ).count()
            
            return {
                'user_id': user_id,
                'name': user.name,
                'email': user.email,
                'total_sessions': total_sessions,
                'total_messages': total_messages,
                'total_job_applications': total_applications,
                'member_since': user.created_at.isoformat() if user.created_at else None
            }