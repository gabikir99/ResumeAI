from utils import Website
from user_intent import get_system_prompt

class GPTService:
    """Service class to handle all GPT-related operations."""
    
    def __init__(self, client, response_handlers=None):
        """Initialize the GPT service with OpenAI client."""
        self.client = client
        self.system_prompt = get_system_prompt()
        self.response_handlers = response_handlers

    def generate_streaming_response(self, intent_info, memory_manager, user_input):
        """Generate a streaming response based on the intent."""
        intent = intent_info['intent']
        args = intent_info.get('args', {})
        
        # Get user info and chat history
        user_info = memory_manager.get_user_info()
        chat_history = memory_manager.get_chat_history()
        
        # Handle simple non-GPT responses
        if intent == 'handle_greeting':
            yield self.response_handlers.handle_greeting(args['greeting'], user_info)
            return
            
        elif intent == 'handle_goodbye':
            yield self.response_handlers.handle_goodbye(args['farewell'], user_info)
            return
            
        elif intent == 'handle_confirmation':
            yield self.response_handlers.handle_confirmation(args['confirmation'], user_info)
            return
            
        elif intent == 'handle_rejection':
            yield self.response_handlers.handle_rejection(args['rejection'], user_info)
            return
            
        elif intent == 'store_personal_info':
            # Store the personal information
            info_type = args['info_type']
            info_value = args['info_value']
            memory_manager.store_user_info(info_type, info_value)
            
            # Create a more specific confirmation message based on what was stored
            if info_type == 'experience':
                yield f"Got it! I've noted that you have {info_value}. This will be helpful for tailoring your resume."
            elif info_type == 'current_role':
                yield f"Perfect! I've noted that you work as {info_value}. Your background will be valuable for your career goals."
            elif info_type == 'name':
                yield f"Nice to meet you, {info_value}! How can I help with your career today?"
            elif info_type == 'career_interest':
                yield f"Excellent! I've noted your interest in {info_value}. I'm here to help you with your job search in this field."
            else:
                yield f"Thanks for sharing that information! I've noted your {info_type}: {info_value}."
            return
            
        elif intent == 'handle_off_topic':
            yield "I'm specialized in helping with resumes, job applications, and career advice. How can I assist you with your career today?"
            return
        
        # Handle GPT-powered responses with streaming
        elif intent == 'process_job_url':
            yield from self.generate_resume_sections_stream(args['url'], user_info, chat_history)
            
        elif intent == 'process_job_description':
            yield from self.process_job_description_stream(args['job_description'], user_info, chat_history)
            
        elif intent == 'rewrite_resume_section':
            section = args['section']
            prompt = f"Please rewrite the {section} section of my resume to make it more effective."
            yield from self.chat_about_resumes_stream(prompt, user_info, chat_history)
            
        elif intent == 'answer_career_question':
            yield from self.chat_about_resumes_stream(args['question'], user_info, chat_history)
            
        elif intent == 'answer_yes_no_question':
            prompt = f"{args['question']}\n\nPlease answer in one word: yes or no."
            yield from self.chat_about_resumes_stream(prompt, user_info, chat_history)

        elif intent == 'answer_with_user_instuctions':
            prompt = f"{args['question']}\n\nPlease answer using this style: {args['style']}."
            yield from self.chat_about_resumes_stream(prompt, user_info, chat_history)
            
        else:
            # Default to chat_about_resumes for unknown intents
            yield from self.chat_about_resumes_stream(user_input, user_info, chat_history)
    
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
    
    def _stream_response_generator(self, messages, temperature=0.3):
        """Generate streaming response from GPT as a generator."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=1500,
                temperature=temperature,
                stream=True
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    yield content  # Yield immediately without printing
                    
        except Exception as e:
            yield f"I apologize, but I encountered an error: {str(e)}"
    
    # Keep the old non-streaming methods for backward compatibility
    def _stream_response(self, messages, temperature=0.3):
        """Generate complete response from GPT (non-streaming)."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=1500,
                temperature=temperature,
                stream=False
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"
    
    # Streaming versions of the methods
    def generate_resume_sections_stream(self, url, user_info=None, chat_history=None):
        """Generate resume sections from a job posting URL with streaming."""
        try:
            website = Website(url)
            messages = self._create_messages(website, is_website=True, user_info=user_info, chat_history=chat_history)
            yield from self._stream_response_generator(messages, temperature=0.3)
        except Exception as e:
            yield f"Error processing URL: {e}"
    
    def process_job_description_stream(self, text, user_info=None, chat_history=None):
        """Process a job description directly from text with streaming."""
        try:
            messages = self._create_messages(text, is_website=False, user_info=user_info, chat_history=chat_history)
            yield from self._stream_response_generator(messages, temperature=0.3)
        except Exception as e:
            yield f"Error processing job description: {e}"
    
    def chat_about_resumes_stream(self, query, user_info=None, chat_history=None):
        """Chat about resume and career-related topics with streaming."""
        try:
            messages = self._create_messages(query, is_website=False, user_info=user_info, chat_history=chat_history)
            yield from self._stream_response_generator(messages, temperature=0.7)
        except Exception as e:
            yield f"Error in chat response: {e}"
    
    # Keep non-streaming versions for other endpoints
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