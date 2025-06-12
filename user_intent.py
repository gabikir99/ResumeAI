import re
from utils import is_valid_url
import json 

# Flexible and adaptive system prompt
SYSTEM_PROMPT = """
You are a friendly and professional career advisor chatbot specializing in resumes, job applications, interviews, and career advice.

IMPORTANT: Always use the user's personal information when available to personalize responses.

## Core Specializations:
- Resume writing and optimization (all sections and formats)
- Job applications and cover letters
- Interview preparation and strategies
- Career development and planning
- Job search strategies and networking
- Salary negotiation and professional growth

## Resume Assistance Philosophy:
You can help with ANY resume section or format the user requests, including but not limited to:
- **Professional summaries** (also called objectives, mission statements, career summaries, professional profiles, etc.)
- **Experience sections** (work history, professional experience, employment history)
- **Skills sections** (core competencies, technical skills, relevant skills, key qualifications)
- **Education sections** (academic background, certifications, training)
- **Achievement highlights** (accomplishments, key achievements, highlights of qualifications)
- **Project sections** (relevant projects, portfolio items, case studies)
- **Additional sections** (volunteer work, publications, awards, etc.)

## Response Guidelines:
- Always provide specific, actionable answers to user questions
- NEVER give generic responses like "I specialize in..." when asked a direct question
- If asked about resume length, give a clear answer about 1-page vs 2-page resumes
- If asked about sections, provide specific guidance
- Use the user's name when available for personalization

## Formatting Guidelines:
Use clear, professional Markdown formatting:
- **Bold** for section headers and key terms
- Bullet points (-) for lists and qualifications
- ## for main sections, ### for subsections
- Emphasize important keywords with **bold**
- Keep content scannable and well-organized

## Personalization Priority:
Always incorporate the user's stored information:
- Use their name naturally in conversations
- Reference their background, experience, and career goals
- Tailor all advice to their specific situation and industry
- Build on previous conversation context

## Boundary Management:
If asked about non-career topics, politely redirect: "I specialize in career and resume assistance. How can I help you with your professional development today?"

## Tone and Approach:
- Friendly, encouraging, and professional
- Direct and actionable advice
- Supportive and confidence-building
- Industry-aware and current with best practices

## IMPORTANT - Avoid Generic Responses:
- NEVER respond with "I'm specialized in helping with resumes..." when asked a specific question
- Always attempt to answer the user's actual question
- If you need more information, ask specific follow-up questions
- Be helpful and specific, not generic and deflecting

Remember: Be helpful and specific. Answer questions directly rather than giving generic responses about your capabilities.
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
    },
    {
    "name": "handle_confirmation",
    "description": "Handle user confirmations like 'yes', 'yeah', 'sure', etc.",
    "parameters": {
        "type": "object",
        "properties": {
            "confirmation": {"type": "string", "description": "The confirmation text"}
        },
        "required": ["confirmation"]
    }
    },
    {
        "name": "handle_rejection",
        "description": "Handle user rejections like 'no', 'not interested', etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "rejection": {"type": "string", "description": "The rejection text"}
            },
            "required": ["rejection"]
        }
    },
    {
    "name": "rewrite_resume_section",
    "description": "Rewrite or regenerate a specific resume section",
    "parameters": {
        "type": "object",
        "properties": {
            "section": {"type": "string", "description": "Which section to rewrite"}
        },
        "required": ["section"]
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
        """Classify intent using GPT with simplified logic."""
        memory_context = ""
        if user_info:
            memory_info = [f"{k}: {v}" for k, v in user_info.items() if v]
            if memory_info:
                memory_context = f"\n\nUser's stored information: {', '.join(memory_info)}"
        
        system_message = f"""
        You are an intent classifier for a career chatbot. Choose the most appropriate function:

        1. **store_personal_info** - If user shares personal details (name, experience, role, interests)
           Examples: "my name is John", "I have 5 years experience", "I work as a developer"

        2. **handle_greeting** - For simple greetings without personal info
           Examples: "hello", "hi there", "good morning"

        3. **handle_goodbye** - For farewells  
           Examples: "goodbye", "thanks", "bye"

        4. **process_job_url** - For valid URLs

        5. **process_job_description** - For long job posting text (50+ words)

        6. **answer_career_question** - For career/resume questions and requests
           Examples: "help with resume", "what should I include", "career advice", "is it better to have 2 pages or one"

        7. **handle_off_topic** - For non-career topics
           Examples: "what's the weather", "how to cook pasta"

        8. **handle_confirmation/rejection** - For simple yes/no responses

        9. **rewrite_resume_section** - For requests to rewrite specific resume sections

        Priority: Personal info > Greetings/Goodbyes > Career questions > Off-topic
        
        IMPORTANT: Career questions should ALWAYS use answer_career_question, not handle_off_topic.{memory_context}
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
            function_args = json.loads(response.choices[0].message.function_call.arguments)
            
            return {
                'intent': function_name,
                'args': function_args,
                'type': 'function_call'
            }
        else:
            # If GPT didn't call a function, fall back to rule-based classification
            print("GPT didn't call a function, falling back to rule-based classification")
            return self._simple_fallback_classification(user_input)
    
    def _simple_fallback_classification(self, user_input):
        """Improved rule-based fallback classification."""
        user_input_lower = user_input.strip().lower()
        
        # PRIORITY 1: Check for personal information FIRST
        personal_patterns = [
            (r'(?:hello|hi|hey)?\s*my name is ([a-zA-Z\s]+)', 'name'),
            (r'(?:hello|hi|hey)?\s*i am ([a-zA-Z\s]+)', 'name'),
            (r'(?:hello|hi|hey)?\s*i\'m ([a-zA-Z\s]+)', 'name'),
            (r'i have (\d+) years? of experience(?:\s+in\s+(.+))?', 'experience'),
            (r'\bi work as (?:a|an)?\s*([a-zA-Z\s]+)', 'current_role'),
            (r'i want to (?:work in|create|build|create a resume for) (.+)', 'career_interest'),
            (r'looking for (.+) (?:job|position|role)', 'career_interest'),
            (r'create (?:a )?resume for (.+)', 'career_interest'),
            (r'interested in (.+) (?:roles?|positions?|jobs?)', 'career_interest'),
        ]
        
        for pattern, info_type in personal_patterns:
            match = re.search(pattern, user_input_lower)
            if match:
                if info_type == 'experience' and len(match.groups()) > 1 and match.group(2):
                    info_value = f"{match.group(1)} years of experience in {match.group(2)}"
                else:
                    info_value = match.group(1).strip()
                    if info_type == 'name':
                        info_value = info_value.title()
                
                return {
                    'intent': 'store_personal_info',
                    'args': {'info_type': info_type, 'info_value': info_value}
                }
        
        # PRIORITY 2: Check for simple greetings (only if no personal info)
        greeting_patterns = [r'\b(hello|hi|hey|good morning|good afternoon|good evening)\b']
        if any(re.search(pattern, user_input_lower) for pattern in greeting_patterns):
            # Make sure it's ONLY a greeting, not combined with other requests
            if len(user_input.split()) <= 3:  # Simple greeting
                return {'intent': 'handle_greeting', 'args': {'greeting': user_input}}
        
        # PRIORITY 3: Check for farewells
        farewell_patterns = [r'\b(goodbye|bye|see you|thanks|thank you)\b']
        if any(re.search(pattern, user_input_lower) for pattern in farewell_patterns):
            if len(user_input.split()) <= 3:  # Simple farewell
                return {'intent': 'handle_goodbye', 'args': {'farewell': user_input}}
        
        # PRIORITY 4: Check for simple confirmations/rejections
        confirmation_words = ['yes', 'yeah', 'yep', 'sure', 'okay', 'ok', 'of course']
        if (user_input_lower.strip() in confirmation_words or 
            user_input_lower in ['yes please', 'sounds good', 'that works']):
            return {'intent': 'handle_confirmation', 'args': {'confirmation': user_input}}
        
        simple_rejections = ['no', 'nope', 'no thanks', 'not interested', 'not really', 'no thank you']
        if (user_input_lower.strip() in simple_rejections and len(user_input.split()) <= 3):
            return {'intent': 'handle_rejection', 'args': {'rejection': user_input}}
        
        # PRIORITY 5: Check for URLs
        if is_valid_url(user_input):
            return {'intent': 'process_job_url', 'args': {'url': user_input}}
        
        # PRIORITY 6: Check for long job descriptions
        job_indicators = ['responsibilities', 'duties', 'qualifications', 'requirements']
        if (len(user_input.split()) > 50 and 
            any(word in user_input_lower for word in job_indicators)):
            return {'intent': 'process_job_description', 'args': {'job_description': user_input}}
        
        # PRIORITY 7: Check for questions about personal info
        personal_questions = ['what is my name', 'what job am i looking for', 'who am i', 'what is my email']
        if any(q in user_input_lower for q in personal_questions):
            return {'intent': 'answer_career_question', 'args': {'question': user_input}}
        
        # PRIORITY 8: Check for specific resume section requests
        resume_sections = ['summary', 'objective', 'experience', 'skills', 'education', 'projects']
        section_keywords = ['rewrite', 'redo', 'change', 'update', 'revise', 'remake']
        
        for section in resume_sections:
            for keyword in section_keywords:
                if keyword in user_input_lower and section in user_input_lower:
                    return {
                        'intent': 'rewrite_resume_section',
                        'args': {'section': section}
                    }
        
        # PRIORITY 9: Check for career-related keywords (be more specific but inclusive)
        specific_career_keywords = [
            'resume', 'cv', 'cover letter', 'job application', 'interview',
            'career advice', 'professional summary', 'work experience',
            'pages', 'sections', 'should i', 'better to', 'make me',
            'help me', 'create', 'write', 'build'
        ]
        
        if any(keyword in user_input_lower for keyword in specific_career_keywords):
            return {'intent': 'answer_career_question', 'args': {'question': user_input}}
        
        # PRIORITY 10: Check for clearly off-topic requests
        off_topic_keywords = ['weather', 'sports', 'cooking', 'movie', 'music', 'recipe', 'game']
        if any(keyword in user_input_lower for keyword in off_topic_keywords):
            return {'intent': 'handle_off_topic', 'args': {'off_topic_query': user_input}}
        
        # DEFAULT: Check if it's a question - if so, assume career-related
        question_indicators = ['how', 'what', 'when', 'where', 'why', 'should', 'can', '?']
        if any(indicator in user_input_lower for indicator in question_indicators):
            return {'intent': 'answer_career_question', 'args': {'question': user_input}}
        
        # Final fallback - if it seems like a request or statement, assume career-related
        return {'intent': 'answer_career_question', 'args': {'question': user_input}}

def get_system_prompt():
    """Get the system prompt."""
    return SYSTEM_PROMPT

def get_intent_functions():
    """Get the intent functions."""
    return INTENT_FUNCTIONS