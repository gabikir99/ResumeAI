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
        print("→ Generating streaming response for intent:", intent_info['intent'])
        
        intent = intent_info['intent']
        args = intent_info.get('args', {})
        
        # Get user info and chat history
        user_info = memory_manager.get_user_info()
        chat_history = memory_manager.get_chat_history()
        
        # Create appropriate messages based on intent
        if intent == 'handle_greeting':
            return self.response_handlers.handle_greeting(args['greeting'], user_info)
            
        elif intent == 'handle_goodbye':
            return self.response_handlers.handle_goodbye(args['farewell'], user_info)
            
        elif intent == 'handle_confirmation':
            return self.response_handlers.handle_confirmation(args['confirmation'], user_info)
            
        elif intent == 'handle_rejection':
            return self.response_handlers.handle_rejection(args['rejection'], user_info)
            
        elif intent == 'process_job_url':
            return self.generate_resume_sections(args['url'], user_info, chat_history)
            
        elif intent == 'process_job_description':
            return self.process_job_description(args['job_description'], user_info, chat_history)
            
        elif intent == 'rewrite_resume_section':
            section = args['section']
            prompt = f"Please rewrite the {section} section of my resume to make it more effective."
            return self.chat_about_resumes(prompt, user_info, chat_history)
            
        elif intent == 'store_personal_info':
            # Store the personal information
            info_type = args['info_type']
            info_value = args['info_value']
            memory_manager.store_user_info(info_type, info_value)
            
            # Create a more specific confirmation message based on what was stored
            if info_type == 'experience':
                return f"Got it! I've noted that you have {info_value}. This will be helpful for tailoring your resume."
            elif info_type == 'current_role':
                return f"Perfect! I've noted that you work as {info_value}. Your background will be valuable for your career goals."
            elif info_type == 'name':
                return f"Nice to meet you, {info_value}! How can I help with your career today?"
            elif info_type == 'career_interest':
                return f"Excellent! I've noted your interest in {info_value}. I'm here to help you with your job search in this field."
            else:
                return f"Thanks for sharing that information! I've noted your {info_type}: {info_value}."
            
        elif intent == 'handle_off_topic':
            return "I'm specialized in helping with resumes, job applications, and career advice. How can I assist you with your career today?"
            
        elif intent == 'answer_career_question':
            return self.chat_about_resumes(args['question'], user_info, chat_history)
            
        else:
            # Default to chat_about_resumes for unknown intents
            return self.chat_about_resumes(user_input, user_info, chat_history)

    
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
        try:
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
            
            return full_response
        except Exception as e:
            print(f"Error in _stream_response: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
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
