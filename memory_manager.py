from langchain.memory import ConversationBufferWindowMemory

class MemoryManager:
    """Manages conversation memory using LangChain's ConversationBufferWindowMemory."""
    
    def __init__(self, k=15):
        """Initialize memory manager with window size k."""
        self.memory = ConversationBufferWindowMemory(k=k)
        self.user_info = {}
    
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
        """Store user information."""
        self.user_info[info_type] = info_value
    
    def get_user_info(self):
        """Get all stored user information."""
        return self.user_info
    
    def get_memory_variables(self):
        """Get memory variables for context inclusion."""
        return self.memory.load_memory_variables({})
