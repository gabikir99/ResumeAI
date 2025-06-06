from datetime import datetime, timedelta
from collections import defaultdict
import json
import threading

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
                    'remaining': self.message_limit
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
                    'remaining': self.message_limit
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
