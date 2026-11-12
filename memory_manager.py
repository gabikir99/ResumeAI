from langchain.memory import ConversationBufferWindowMemory
import uuid
from datetime import datetime
from typing import Optional


class MemoryManager:
    """Manage conversation memory with optional database persistence."""

    def __init__(self, k: int = 30, session_id: Optional[str] = None, db_service=None, user_id: Optional[int] = None):
        """Initialize memory manager with window size k and optional session ID."""
        self.k = k
        self.db_service = db_service
        self.user_id = user_id

        if session_id:
            self.session_id = session_id
            if self.db_service and not self.db_service.get_chat_session(session_id):
                # Create a session using provided ID so rate limiting works
                self.db_service.create_chat_session(user_id=self.user_id, session_id=session_id)
        else:
            if self.db_service:
                self.session_id = self.db_service.create_chat_session(user_id=self.user_id)
            else:
                self.session_id = str(uuid.uuid4())

        self.session_start = datetime.now()
        self._reset_memory()

        if self.db_service:
            self._load_history_from_db()
            if self.user_id:
                self._load_user_info_from_db()
    
    def _reset_memory(self):
        """Reset all memory components."""
        self.memory = ConversationBufferWindowMemory(k=self.k)
        self.user_info = {}
        print(f"🔄 New session started: {self.session_id[:8]}...")
    
    def _load_history_from_db(self):
        """Load previous chat history from the database if available."""
        try:
            messages = self.db_service.get_session_messages(self.session_id, limit=1000)
            user_msg = None
            for msg in messages:
                if msg['message_type'] == 'user':
                    user_msg = msg['content']
                elif msg['message_type'] == 'assistant' and user_msg is not None:
                    self.memory.save_context({"input": user_msg}, {"output": msg['content']})
                    user_msg = None
        except Exception as e:
            print(f"⚠️  Failed to load history for {self.session_id[:8]}: {e}")

    def _load_user_info_from_db(self):
        """Load stored user information from the database if available."""
        try:
            profile = self.db_service.get_user_profile(self.user_id)
            if profile:
                if profile.get('current_role'):
                    self.user_info['current_role'] = profile['current_role']
                if profile.get('experience'):
                    self.user_info['experience'] = profile['experience']
                if profile.get('skills'):
                    self.user_info['skills'] = profile['skills']
                if profile.get('education'):
                    self.user_info['education'] = profile['education']
                if profile.get('career_interests'):
                    self.user_info['career_interest'] = profile['career_interests']
                if profile.get('other_info'):
                    for k, v in profile['other_info'].items():
                        self.user_info[k] = v
        except Exception as e:
            print(f"⚠️  Failed to load user info for {self.user_id}: {e}")

    def start_new_session(self):
        """Start a completely new session with fresh memory."""
        if self.db_service:
            self.session_id = self.db_service.create_chat_session(user_id=self.user_id)
        else:
            self.session_id = str(uuid.uuid4())
        self.session_start = datetime.now()
        self._reset_memory()
        return self.session_id
    
    def add_message(self, human_message: str, ai_message: str):
        """Add a message pair to memory and optionally store in the database."""
        self.memory.save_context({"input": human_message}, {"output": ai_message})
        if self.db_service:
            try:
                self.db_service.save_message(self.session_id, "user", human_message)
                self.db_service.save_message(self.session_id, "assistant", ai_message)
            except Exception as e:
                print(f"⚠️  Failed to save message: {e}")
    
    def get_chat_history(self) -> str:
        """Get the chat history as a formatted string."""
        return self.memory.buffer
    
    def store_user_info(self, info_type: str, info_value: str):
        """Store user info in memory and persist if possible."""
        self.user_info[info_type] = info_value
        if self.db_service and self.user_id:
            try:
                self.db_service.update_user_profile(self.user_id, info_type, info_value)
            except Exception as e:
                print(f"⚠️  Failed to store user info: {e}")
        print(f"📝 Stored {info_type} for current session")
    
    def get_user_info(self):
        """Return stored user information."""
        return self.user_info
    
    def get_memory_variables(self):
        """Get memory variables for context inclusion."""
        return self.memory.load_memory_variables({})
    
    def get_session_info(self):
        """Get information about current session."""
        return {
            'session_id': self.session_id,
            'start_time': self.session_start,
            'user_info_count': len(self.user_info),
            'chat_history_length': len(self.get_chat_history().split()) if self.get_chat_history() else 0
        }
    
    def clear_user_info_only(self):
        """Clear only user info but keep chat history."""
        self.user_info = {}
        print("🧹 User information cleared (chat history preserved)")
    
    def clear_chat_history_only(self):
        """Clear only chat history but keep user info."""
        self.memory = ConversationBufferWindowMemory(k=self.k)
        if self.db_service:
            try:
                self.db_service.clear_session_messages(self.session_id)
            except Exception as e:
                print(f"⚠️  Failed to clear messages: {e}")
        print("🧹 Chat history cleared (user information preserved)")
    
    def export_session_data(self):
        """Export current session data for backup/analysis."""
        return {
            'session_id': self.session_id,
            'session_start': self.session_start.isoformat(),
            'user_info': self.user_info.copy(),
            'chat_history': self.get_chat_history(),
            'message_count': len(self.memory.chat_memory.messages) if hasattr(self.memory, 'chat_memory') else 0
        }
    
    def import_session_data(self, session_data):
        """Import session data for restoration."""
        self.session_id = session_data.get('session_id', str(uuid.uuid4()))
        self.session_start = datetime.fromisoformat(
            session_data.get('session_start', datetime.now().isoformat())
        )
        self.user_info = session_data.get('user_info', {})
        
        # Recreate memory with chat history if available
        self.memory = ConversationBufferWindowMemory(k=self.k)
        if session_data.get('chat_history'):
            # Note: This is a simplified restoration - full restoration would need message pairs
            print(f"📥 Session data imported: {self.session_id[:8]}...")