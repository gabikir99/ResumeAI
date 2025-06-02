from langchain.memory import ConversationBufferWindowMemory
import uuid
from datetime import datetime

class MemoryManager:
    """Manages conversation memory with session control."""
    
    def __init__(self, k=15, session_id=None):
        """Initialize memory manager with window size k and optional session ID."""
        self.k = k
        self.session_id = session_id or str(uuid.uuid4())
        self.session_start = datetime.now()
        self._reset_memory()
    
    def _reset_memory(self):
        """Reset all memory components."""
        self.memory = ConversationBufferWindowMemory(k=self.k)
        self.user_info = {}
        print(f"🔄 New session started: {self.session_id[:8]}...")
    
    def start_new_session(self):
        """Start a completely new session with fresh memory."""
        self.session_id = str(uuid.uuid4())
        self.session_start = datetime.now()
        self._reset_memory()
        return self.session_id
    
    def add_message(self, human_message, ai_message):
        """Add a message pair to memory."""
        self.memory.save_context(
            {"input": human_message},
            {"output": ai_message}
        )
    
    def get_chat_history(self):
        """Get the chat history as a formatted string."""
        return self.memory.buffer
    
    def store_user_info(self, info_type, info_value):
        """Store user information in current session only."""
        self.user_info[info_type] = info_value
        print(f"📝 Stored {info_type} for current session")
    
    def get_user_info(self):
        """Get all stored user information for current session."""
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
        """Import session data (for testing or restoration)."""
        self.session_id = session_data.get('session_id', str(uuid.uuid4()))
        self.session_start = datetime.fromisoformat(session_data.get('session_start', datetime.now().isoformat()))
        self.user_info = session_data.get('user_info', {})
        
        # Recreate memory with chat history if available
        self.memory = ConversationBufferWindowMemory(k=self.k)
        if session_data.get('chat_history'):
            # Note: This is a simplified restoration - full restoration would need message pairs
            print(f"📥 Session data imported: {self.session_id[:8]}...")