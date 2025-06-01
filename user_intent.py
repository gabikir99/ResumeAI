import re
from utils import is_valid_url

# System prompt for the resume advisor chatbot
SYSTEM_PROMPT = """
You are a friendly and professional career advisor chatbot specializing ONLY in resumes, job applications, interviews, and career advice.

IMPORTANT: Always use the user's personal information when available to personalize responses.

IMPORTANT BOUNDARIES: You should ONLY help with career-related topics including:
- Resume writing and tailoring
- Job applications and cover letters
- Interview preparation
- Career advice and development
- Job search strategies
- Professional networking
- Salary negotiation

If a user asks about topics unrelated to careers, politely redirect them back to career-related assistance.

When a user provides a job description, help them by generating:

1. An Objective — a brief 1–2 sentence summary of why they are a great fit for the role.

2. A list of exactly 6-7 Highlights of Qualifications — specific, relevant points about their skills, achievements, or experience that match the job.

3. A categorized list of Relevant Skills — organize skills into logical groups based on the job requirements.

IMPORTANT: Do not use any Markdown formatting in your responses. Present all text as plain text only.

PERSONALIZATION: Always incorporate the user's stored personal information naturally into your responses. If you know their name, use it. If you know their background, reference it appropriately.
"""

INTENT_FUNCTIONS = [
    {
        "name": "handle_greeting",
        "description": "Respond to user greetings",
        "parameters": {
            "type": "object",
            "properties": {
                "greeting": {"type": "string", "description": "The greeting message"}
            },
            "required": ["greeting"]
        }
    },
    {
        "name": "handle_goodbye",
        "description": "Respond to user farewells",
        "parameters": {
            "type": "object",
            "properties": {
                "farewell": {"type": "string", "description": "The farewell message"}
            },
            "required": ["farewell"]
        }
    },
    {
        "name": "process_job_url",
        "description": "Process a job posting URL",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The job posting URL"}
            },
            "required": ["url"]
        }
    },
    {
        "name": "process_job_description",
        "description": "Process job description text",
        "parameters": {
            "type": "object",
            "properties": {
                "job_description": {"type": "string", "description": "The job description text"}
            },
            "required": ["job_description"]
        }
    },
    {
        "name": "answer_career_question",
        "description": "Answer career-related questions",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "The career question"}
            },
            "required": ["question"]
        }
    },
    {
        "name": "store_personal_info",
        "description": "Store personal information",
        "parameters": {
            "type": "object",
            "properties": {
                "info_type": {
                    "type": "string",
                    "enum": ["name", "current_role", "experience", "skills", "education", "other", "career_interest"]
                },
                "info_value": {"type": "string", "description": "The information value"}
            },
            "required": ["info_type", "info_value"]
        }
    },
    {
        "name": "handle_off_topic",
        "description": "Handle off-topic questions",
        "parameters": {
            "type": "object",
            "properties": {
                "off_topic_query": {"type": "string", "description": "The off-topic query"}
            },
            "required": ["off_topic_query"]
        }
    }
]

class IntentClassifier:
    """Classify user intents using GPT with fallback to simple rules."""
    
    def __init__(self, client):
        """Initialize the intent classifier."""
        self.client = client
    
    def classify_intent(self, user_input, user_info=None):
        """Classify the user's intent."""
        try:
            return self._classify_with_gpt(user_input, user_info)
        except Exception as e:
            print(f"GPT classification failed: {e}. Using fallback.")
            return self._simple_fallback_classification(user_input)
    
    def _classify_with_gpt(self, user_input, user_info=None):
        """Classify intent using GPT."""
        memory_context = ""
        if user_info:
            memory_info = [f"{k}: {v}" for k, v in user_info.items() if v]
            if memory_info:
                memory_context = f"\n\nUser's stored information: {', '.join(memory_info)}"
        
        system_message = f"""
        You are an intent classifier for a career advice chatbot. Analyze the user's input and determine the most appropriate action.
        
        Guidelines:
        1. If it's a greeting, use handle_greeting
        2. If it's a farewell, use handle_goodbye
        3. If it's a valid URL, use process_job_url
        4. If it's a long job description text, use process_job_description
        5. If it's a career-related question, use answer_career_question
        6. If sharing personal info (name, experience, skills, career interests, etc.), use store_personal_info
        7. If asking about stored info or personal questions like "what is my name", use answer_career_question
        8. If completely off-topic, use handle_off_topic
        
        For personal info detection:
        - "my name is X" or "i am X" → store as name
        - "i want to work in X" or "looking for X job" → store as career_interest
        - "i have X experience" → store as experience
        - "i work as X" → store as current_role{memory_context}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_input}
            ],
            functions=INTENT_FUNCTIONS,
            function_call="auto",
            temperature=0.1
        )
        
        if response.choices[0].message.function_call:
            function_name = response.choices[0].message.function_call.name
            function_args = eval(response.choices[0].message.function_call.arguments)
            
            return {
                'intent': function_name,
                'args': function_args,
                'type': 'function_call'
            }
        else:
            return {
                'intent': 'general_response',
                'message': response.choices[0].message.content,
                'type': 'text_response'
            }
    
    def _simple_fallback_classification(self, user_input):
        """Simple rule-based fallback classification."""
        user_input_lower = user_input.strip().lower()
        
        # Check for greetings
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        if any(greeting in user_input_lower for greeting in greetings):
            return {'intent': 'handle_greeting', 'args': {'greeting': user_input}}
        
        # Check for farewells
        farewells = ['goodbye', 'bye', 'see you', 'thanks', 'thank you']
        if any(farewell in user_input_lower for farewell in farewells):
            return {'intent': 'handle_goodbye', 'args': {'farewell': user_input}}
        
        # Check for URLs
        if is_valid_url(user_input):
            return {'intent': 'process_job_url', 'args': {'url': user_input}}
        
        # Check for personal information with improved patterns
        personal_patterns = [
            (r'my name is ([a-zA-Z\s]+)', 'name'),
            (r'i am ([a-zA-Z\s]+)', 'name'),
            (r'i have (\d+) years? of experience(?:\s+in\s+(.+))?', 'experience'),
            (r'i work as a?n? (.+)', 'current_role'),
            (r'i want to (?:work in|create|build|create a resume for) (.+)', 'career_interest'),
            (r'looking for (.+) (?:job|position|role)', 'career_interest'),
        ]
        
        for pattern, info_type in personal_patterns:
            match = re.search(pattern, user_input_lower)
            if match:
                if info_type == 'experience' and len(match.groups()) > 1 and match.group(2):
                    # Capture both years and field of experience
                    info_value = f"{match.group(1)} years of experience in {match.group(2)}"
                else:
                    info_value = match.group(1).strip()
                return {
                    'intent': 'store_personal_info',
                    'args': {'info_type': info_type, 'info_value': info_value}
                }
        
        # Check for questions about personal info
        personal_questions = ['what is my name', 'what job am i looking for', 'who am i']
        if any(q in user_input_lower for q in personal_questions):
            return {'intent': 'answer_career_question', 'args': {'question': user_input}}
        
        # Check for job description (long text with job-related keywords)
        job_indicators = ['job description', 'responsibilities', 'requirements', 'qualifications']
        if len(user_input.split()) > 50 and any(indicator in user_input_lower for indicator in job_indicators):
            return {'intent': 'process_job_description', 'args': {'job_description': user_input}}
        
        # Default to career question
        return {'intent': 'answer_career_question', 'args': {'question': user_input}}

def get_system_prompt():
    """Get the system prompt."""
    return SYSTEM_PROMPT

def get_intent_functions():
    """Get the intent functions."""
    return INTENT_FUNCTIONS