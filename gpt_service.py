from utils import Website
from user_intent import get_system_prompt

class GPTService:
    """Service class to handle all GPT-related operations."""
    
    def __init__(self, client):
        """Initialize the GPT service with OpenAI client."""
        self.client = client
        self.system_prompt = get_system_prompt()

    def generate_streaming_response(self, intent_info, memory_manager, user_input):
     print("→ Generating streaming response for input:", user_input)

     messages = [
        {"role": "system", "content": "You are a helpful resume assistant."},
        {"role": "user", "content": user_input}
     ]

     try:
        stream = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            stream=True
        )

        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print("→ Chunk received:", repr(content), flush=True)
                yield content
            else:
                print("→ Chunk with no content:", chunk)

     except Exception as e:
        print("→ Streaming error:", e, flush=True)
        yield f"\n[Error generating response: {str(e)}]"

    
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
                # Create more natural descriptions
                if key == 'name':
                    memory_items.append(f"The user's name is {value}")
                elif key == 'career_interest':
                    memory_items.append(f"The user wants to work in {value}")
                elif key == 'current_role':
                    memory_items.append(f"The user currently works as {value}")
                elif key == 'experience':
                    memory_items.append(f"The user has {value} of experience")
                else:
                    memory_items.append(f"The user's {key} is {value}")
        
        if memory_items:
            memory_context = "IMPORTANT - User's Personal Information:\n" + "\n".join(memory_items)
            memory_context += "\n\nAlways use this information to personalize your responses. Address the user by name when appropriate and reference their background naturally."
        else:
            memory_context = "No personal information stored yet."
        
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
        
        return full_response  # Return the full response instead of empty string
    
    def generate_resume_sections(self, url, user_info=None, chat_history=None):
        """Generate resume sections from a job posting URL."""
        try:
            website = Website(url)
            messages = self._create_messages(website, is_website=True, user_info=user_info, chat_history=chat_history)
            return self._stream_response(messages, temperature=0.3)
        except Exception as e:
            return f"Error processing URL: {e}"
    
    def process_job_description(self, text, user_info=None, chat_history=None):
        """Process a job description directly from text."""
        try:
            messages = self._create_messages(text, is_website=False, user_info=user_info, chat_history=chat_history)
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
