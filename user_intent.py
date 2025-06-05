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

## Adaptive Response Approach:
- **Recognize synonyms**: Understand that "summary statement" = "objective" = "professional profile" = "mission statement"
- **Match user terminology**: Use the same words the user uses (if they say "summary," respond with "summary")
- **Flexible formatting**: Adapt to different resume styles and user preferences
- **Context-aware**: Tailor advice based on industry, career level, and specific goals

## When Helping with Job-Related Content:
- Analyze job descriptions and requirements thoroughly
- Generate 6-7 specific, relevant qualification points that match the role
- Organize skills into logical, industry-appropriate categories
- Create compelling, personalized content using stored user information
- Suggest improvements and optimizations based on best practices

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

## IMPORTANT - Avoid Hallucination:
- NEVER make up information about the user that hasn't been provided
- If you need specific information to create a resume section or provide tailored advice, ASK the user directly
- Be transparent about what information you need to provide quality assistance
- For example: "To create an effective professional summary, I'll need to know your years of experience, current role, and key skills. Could you share those details with me?"
- Always check if you have enough context before generating content
- If unsure about industry-specific details, ask clarifying questions

Remember: Be flexible and adaptive. The user knows what they need - your job is to provide expert guidance regardless of the specific terminology they use.
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
        """Classify intent using GPT."""
        memory_context = ""
        if user_info:
            memory_info = [f"{k}: {v}" for k, v in user_info.items() if v]
            if memory_info:
                memory_context = f"\n\nUser's stored information: {', '.join(memory_info)}"
        
        system_message = f"""
        You are an intent classifier for a career advice chatbot. Analyze the user's input and determine the most appropriate action.
        
        Guidelines:
        1. **HIGHEST PRIORITY - Personal Info Storage**: If ANY personal information is mentioned, ALWAYS use store_personal_info, even if combined with greetings
        2. If it's a greeting without personal info (hello, hi, hey), use handle_greeting
        3. If it's a farewell (goodbye, bye, thanks), use handle_goodbye
        4. If it's a valid URL, use process_job_url
        5. If it's a long job description text (50+ words with job keywords), use process_job_description
        6. If asking about stored info ("what is my name", "who am i"), use answer_career_question
        
        **CRITICAL EXAMPLES for store_personal_info:**
        - "hello my name is John" → store_personal_info with name="John"
        - "hi I'm Sarah" → store_personal_info with name="Sarah"
        - "my name is Alex" → store_personal_info with name="Alex"
        - "I have 5 years experience" → store_personal_info with experience
        - "I work as a developer" → store_personal_info with current_role
        - "I want to work in data science" → store_personal_info with career_interest
        - "create resume for marketing" → store_personal_info with career_interest
        
        **NEVER** classify inputs containing personal information as anything other than store_personal_info.
        
        CAREER-RELATED REQUESTS (use answer_career_question):
        - Resume help: "create resume", "write objective", "mission statement", "summary statement", "professional profile"
        - Career advice: "career guidance", "job search help", "interview tips"
        - Any request for resume sections: objective, summary, skills, experience, qualifications
        - Career questions: "how to", "help with", "advice on" + career topics
        
        ONLY use handle_off_topic for completely non-career topics like weather, sports, cooking, etc.
        
        Remember: Personal information detection takes absolute priority over everything else.{memory_context}
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
        """Simple rule-based fallback classification."""
        user_input_lower = user_input.strip().lower()
        
        # PRIORITY: Check for personal information FIRST (even if combined with greetings)
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
                        info_value = info_value.title()  # Capitalize name properly
                
                return {
                    'intent': 'store_personal_info',
                    'args': {'info_type': info_type, 'info_value': info_value}
                }
        
        # Check for greetings (only if no personal info was found)
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        if any(re.search(rf'\b{greeting}\b', user_input_lower) for greeting in greetings):
            return {'intent': 'handle_greeting', 'args': {'greeting': user_input}}
        
        # Check for farewells
        farewells = ['goodbye', 'bye', 'see you', 'thanks', 'thank you']
        if any(farewell in user_input_lower for farewell in farewells):
            return {'intent': 'handle_goodbye', 'args': {'farewell': user_input}}
        
        # Check for URLs
        if is_valid_url(user_input):
            return {'intent': 'process_job_url', 'args': {'url': user_input}}
        
        # Check for questions about personal info
        personal_questions = ['what is my name', 'what job am i looking for', 'who am i']
        if any(q in user_input_lower for q in personal_questions):
            return {'intent': 'answer_career_question', 'args': {'question': user_input}}
        
        # IMPROVED: Check for career-related requests (this was missing!)
        career_keywords = [
            'resume', 'cv', 'objective', 'summary', 'mission statement', 'professional profile',
            'cover letter', 'job application', 'interview', 'career', 'skills', 'experience',
            'qualifications', 'achievements', 'work history', 'professional', 'statement',
            'help me', 'create', 'write', 'build', 'develop'
        ]
        
        # If any career keyword is found, it's likely a career question
        if any(keyword in user_input_lower for keyword in career_keywords):
            return {'intent': 'answer_career_question', 'args': {'question': user_input}}
        
        # Check for job description (long text with job-related keywords)
        job_indicators = ['job description', 'responsibilities', 'requirements', 'qualifications']
        if len(user_input.split()) > 50 and any(word in user_input_lower for word in ['responsibilities', 'duties', 'qualifications']):
            return {'intent': 'process_job_description', 'args': {'job_description': user_input}}

        # Check for completely off-topic (non-career) requests
        off_topic_keywords = ['weather', 'sports', 'cooking', 'movie', 'music', 'game', 'food', 'travel']
        if any(keyword in user_input_lower for keyword in off_topic_keywords):
            return {'intent': 'handle_off_topic', 'args': {'off_topic_query': user_input}}
        
        confirmations = ['yes', 'yeah', 'yep', 'sure', 'okay', 'ok', 'of course', 'please do', 'go ahead']
        if user_input_lower.strip() in confirmations:
            return {'intent': 'handle_confirmation', 'args': {'confirmation': user_input}}

        rejections = ['no', 'not interested', 'no thanks', 'nope', 'not really', 'not at this time']
        if user_input_lower.strip() in rejections:
            return {'intent': 'handle_rejection', 'args': {'rejection': user_input}}
        
        resume_rewrite_keywords = ['redo', 'remake', 'rewrite', 'revise', 'change', 'edit']
        resume_sections = ['summary', 'objective', 'experience', 'skills', 'education', 'projects', 'achievements']

        for keyword in resume_rewrite_keywords:
            for section in resume_sections:
                if keyword in user_input_lower and section in user_input_lower:
                    return {
                        'intent': 'rewrite_resume_section',
                        'args': {'section': section}
                    }
        
        if any(word in user_input_lower for word in resume_rewrite_keywords):
            return {'intent': 'answer_career_question', 'args': {'question': user_input}}


        # Default to career question (assume career-related unless clearly off-topic)
        return {'intent': 'answer_career_question', 'args': {'question': user_input}}

def get_system_prompt():
    """Get the system prompt."""
    return SYSTEM_PROMPT

def get_intent_functions():
    """Get the intent functions."""
    return INTENT_FUNCTIONS