from utils import Website
from user_intent import get_system_prompt

class GPTService:
    """Service class to handle all GPT-related operations."""
    
    def __init__(self, client):
        """Initialize the GPT service with OpenAI client."""
        self.client = client
        self.system_prompt = get_system_prompt()
    
    def _create_messages(self, content, is_website=True, user_info=None, chat_history=None):
        """Create message format for GPT API."""
        messages = [
            {"role": "system", "content": self.system_prompt},
        ]
        
        # Add user info context if available
        if user_info and len(user_info) > 0:
            memory_context = self._build_memory_context(user_info)
            messages.append({"role": "system", "content": memory_context})
        
        # Add chat history if available
        if chat_history:
            messages.append({"role": "system", "content": f"Previous conversation:\n{chat_history}"})
        
        # Add current content
        if is_website:
            messages.append({"role": "user", "content": content.user_prompt()})
        else:
            messages.append({"role": "user", "content": content})
        
        return messages
    
    def _build_memory_context(self, user_info):
        """Build memory context string from user info."""
        memory_items = []
        for key, value in user_info.items():
            if value:
                memory_items.append(f"{key}: {value}")
        
        memory_context = "User information: " + ", ".join(memory_items)
        memory_context += "\n\nIf the user asks about their personal information, respond with the stored information naturally."
        
        return memory_context
    
    def _stream_response(self, messages, temperature=0.3):
        """Generate streaming response from GPT."""
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=1500,
            temperature=temperature,
            stream=True
        )
        
        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                from utils import print_streaming
                print_streaming(content)
        
        return ""
    
    def generate_resume_sections(self, url, chat_history=None):
        """Generate resume sections from a job posting URL."""
        try:
            website = Website(url)
            messages = self._create_messages(website, is_website=True, chat_history=chat_history)
            return self._stream_response(messages, temperature=0.3)
        except Exception as e:
            return f"Error processing URL: {e}"
    
    def process_job_description(self, text, chat_history=None):
        """Process a job description directly from text."""
        try:
            messages = self._create_messages(text, is_website=False, chat_history=chat_history)
            return self._stream_response(messages, temperature=0.3)
        except Exception as e:
            return f"Error processing job description: {e}"
    
    def chat_about_resumes(self, query, user_info=None, chat_history=None):
        """Chat about resume and career-related topics."""
        try:
            messages = self._create_messages(query, is_website=False, user_info=user_info, chat_history=chat_history)
            return self._stream_response(messages, temperature=0.7)
        except Exception as e:
            return f"Error in chat response: {e}"
