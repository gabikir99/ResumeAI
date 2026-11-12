from datetime import datetime, timedelta, timezone
import json
import threading
from database.connection import get_db_session, init_database
from database.models import ChatSession

# Ensure the required tables exist when this module is imported
init_database()

class InMemoryRateLimiter:
    """Simple in-memory rate limiter - no database required!"""
    
    def __init__(self, message_limit=50, reset_period_hours=24):
        """
        Initialize the rate limiter with in-memory storage.
        
        Args:
            message_limit: Maximum messages allowed per session (default: 50)
            reset_period_hours: Hours before the counter resets (default: 24)
        """
        self.message_limit = message_limit  
        self.reset_period = timedelta(hours=reset_period_hours) 
        
        # In-memory storage
        self.sessions = {}  # {session_id: {'count': int, 'first_message': datetime}}
        self.lock = threading.Lock()  # Thread safety
    
    def check_limit(self, session_id):
        """
        Check if session has reached message limit.
        
        Returns:
            dict: {
                'allowed': bool,
                'current_count': int,
                'limit': int,
                'reset_time': datetime or None,
                'remaining': int,
                'time_until_reset': str (only if reset_time is not None)
            }
        """
        with self.lock:
            if session_id not in self.sessions:
                # New session
                return {
                    'allowed': True,
                    'current_count': 0,
                    'limit': self.message_limit,
                    'reset_time': None,
                    'remaining': self.message_limit,
                    'time_until_reset': None
                }
            
            session = self.sessions[session_id]
            reset_time = session['first_message'] + self.reset_period
            
            # Check if we should reset
            if datetime.now() >= reset_time:
                del self.sessions[session_id]
                return {
                    'allowed': True,
                    'current_count': 0,
                    'limit': self.message_limit,
                    'reset_time': None,
                    'remaining': self.message_limit,
                    'time_until_reset': None
                }
            
            current_count = session['count']
            allowed = current_count < self.message_limit
            remaining = max(0, self.message_limit - current_count)
            
            # Calculate time until reset
            time_until_reset = reset_time - datetime.now()
            
            return {
                'allowed': allowed,
                'current_count': current_count,
                'limit': self.message_limit,
                'reset_time': reset_time,
                'remaining': remaining,
                'time_until_reset': str(time_until_reset).split('.')[0]
            }
    
    def increment_count(self, session_id):
        """Increment message count for session."""
        with self.lock:
            if session_id not in self.sessions:
                self.sessions[session_id] = {
                    'count': 1,
                    'first_message': datetime.now()
                }
                return 1
            else:
                self.sessions[session_id]['count'] += 1
                return self.sessions[session_id]['count']
    
    def reset_session(self, session_id):
        """Reset message count for a session."""
        with self.lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
    
    def get_session_stats(self, session_id):
        """Get detailed statistics for a session."""
        stats = self.check_limit(session_id)
        
        # Add time until reset
        if stats['reset_time']:
            time_until_reset = stats['reset_time'] - datetime.now()
            stats['time_until_reset'] = str(time_until_reset).split('.')[0]
        else:
            stats['time_until_reset'] = None
        
        return stats
    
    def get_all_active_sessions(self):
        """Get all active sessions with their message counts."""
        with self.lock:
            sessions = []
            for session_id, data in self.sessions.items():
                sessions.append({
                    'session_id': session_id,
                    'message_count': data['count'],
                    'first_message_time': data['first_message'].isoformat()
                })
            return sessions
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        with self.lock:
            current_time = datetime.now()
            expired = []
            
            for session_id, data in self.sessions.items():
                reset_time = data['first_message'] + self.reset_period
                if current_time >= reset_time:
                    expired.append(session_id)
            
            for session_id in expired:
                del self.sessions[session_id]


class DatabaseRateLimiter:
    """Rate limiter that stores counts in the database."""

    def __init__(self, message_limit=50, reset_period_hours=24):
        # Ensure database tables are created
        init_database()
        self.message_limit = message_limit
        self.reset_period = timedelta(hours=reset_period_hours)

    def _get_session(self, session, session_id):
        return session.query(ChatSession).filter(ChatSession.session_id == session_id).first()

    def check_limit(self, session_id):
        with get_db_session() as session:
            chat_session = self._get_session(session, session_id)
            if not chat_session:
                return {
                    'allowed': True,
                    'current_count': 0,
                    'limit': self.message_limit,
                    'reset_time': None,
                    'remaining': self.message_limit,
                    'time_until_reset': None
                }

            first_time = chat_session.first_message_time
            if first_time and first_time.tzinfo is None:
                first_time = first_time.replace(tzinfo=timezone.utc)
            if first_time:
                reset_time = first_time + self.reset_period
                if datetime.now(timezone.utc) >= reset_time:
                    chat_session.message_count = 0
                    chat_session.first_message_time = None
                    session.flush()
                    return {
                        'allowed': True,
                        'current_count': 0,
                        'limit': self.message_limit,
                        'reset_time': None,
                        'remaining': self.message_limit
                    }
            else:
                reset_time = None


            count = chat_session.message_count or 0
            allowed = count < self.message_limit
            remaining = max(0, self.message_limit - count)
            time_until_reset = None
            if reset_time:
                time_until_reset = str(reset_time - datetime.now(timezone.utc)).split('.')[0]

            return {
                'allowed': allowed,
                'current_count': count,
                'limit': self.message_limit,
                'reset_time': reset_time,
                'remaining': remaining,
                'time_until_reset': time_until_reset
            }

    def increment_count(self, session_id):
        with get_db_session() as session:
            chat_session = self._get_session(session, session_id)
            if not chat_session:
                chat_session = ChatSession.create_session()
                chat_session.session_id = session_id
                session.add(chat_session)
            if chat_session.first_message_time is None:
                chat_session.first_message_time = datetime.now(timezone.utc)
            chat_session.message_count = (chat_session.message_count or 0) + 1
            session.flush()
            return chat_session.message_count

    def reset_session(self, session_id):
        with get_db_session() as session:
            chat_session = self._get_session(session, session_id)
            if chat_session:
                chat_session.message_count = 0
                chat_session.first_message_time = None
                session.flush()

    def get_session_stats(self, session_id):
        return self.check_limit(session_id)

    def get_all_active_sessions(self):
        with get_db_session() as session:
            sessions = session.query(ChatSession).filter(ChatSession.message_count > 0).all()
            return [
                {
                    'session_id': s.session_id,
                    'message_count': s.message_count,
                    'first_message_time': s.first_message_time.isoformat() if s.first_message_time else None
                }
                for s in sessions
            ]

    def cleanup_expired_sessions(self):
        with get_db_session() as session:
            now = datetime.now(timezone.utc)
            for s in session.query(ChatSession).filter(ChatSession.first_message_time != None).all():
                first_time = s.first_message_time
                if first_time and first_time.tzinfo is None:
                    first_time = first_time.replace(tzinfo=timezone.utc)
                reset_time = first_time + self.reset_period
                if now >= reset_time:
                    s.message_count = 0
                    s.first_message_time = None
            session.flush()