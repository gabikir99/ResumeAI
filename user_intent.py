import re
from urllib.parse import urlparse

# System prompt for the resume advisor chatbot
SYSTEM_PROMPT = """
You are a friendly and professional career advisor chatbot specializing ONLY in resumes, job applications, interviews, and career advice.

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

3. A categorized list of Relevant Skills — organize skills into logical groups based on the job requirements. Create categories that make sense for the specific role, such as:
- For technical roles: Technical Skills, Programming Languages, Software/Tools
- For marketing roles: Marketing Platforms, Analytics Tools, Creative Software
- For healthcare roles: Clinical Skills, Medical Software, Certifications
- For finance roles: Financial Software, Analysis Tools, Compliance Knowledge
- For education roles: Teaching Methods, Educational Technology, Curriculum Development
- And so on...

Choose 3-5 relevant categories based on what the job posting emphasizes. List the skills in each group separated by commas.

IMPORTANT: Do not use any Markdown formatting in your responses. Do not use asterisks (*) around section titles or for emphasis. Do not use backticks (`) for code. Do not use any special formatting characters. Present all text as plain text only.

PERSONALIZATION: If the user has previously shared personal information (name, current role, experience, skills, etc.), incorporate this information naturally into your responses to make them more personalized and relevant.
"""

INTENT_FUNCTIONS = [
    {
        "name": "process_job_url",
        "description": "Process a job posting URL to generate tailored resume sections. Use this when the user provides a URL to a job posting.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The job posting URL to analyze"
                }
            },
            "required": ["url"],
            "additionalProperties": False
        }
    },
    {
        "name": "process_job_description",
        "description": "Process a job description text to generate tailored resume sections. Use this when the user pastes a job description or job posting text.",
        "parameters": {
            "type": "object",
            "properties": {
                "job_description": {
                    "type": "string",
                    "description": "The job description text to analyze"
                }
            },
            "required": ["job_description"],
            "additionalProperties": False
        }
    },
    {
        "name": "answer_career_question",
        "description": "Answer questions about resumes, job applications, interviews, or career advice. Use this for any career-related questions.",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The career-related question to answer"
                }
            },
            "required": ["question"],
            "additionalProperties": False
        }
    },
    {
        "name": "store_personal_info",
        "description": "Store personal information shared by the user for future personalization. Use this when the user shares their name, current role, experience, skills, or other personal details.",
        "parameters": {
            "type": "object",
            "properties": {
                "info_type": {
                    "type": "string",
                    "enum": ["name", "current_role", "experience", "skills", "education", "other"],
                    "description": "The type of personal information being shared"
                },
                "info_value": {
                    "type": "string",
                    "description": "The actual information being shared"
                }
            },
            "required": ["info_type", "info_value"],
            "additionalProperties": False
        }
    },
    {
        "name": "handle_off_topic",
        "description": "Handle questions that are not related to careers, resumes, or job applications. Use this for questions about cooking, exercise, entertainment, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "off_topic_query": {
                    "type": "string",
                    "description": "The off-topic question or statement"
                }
            },
            "required": ["off_topic_query"],
            "additionalProperties": False
        }
    }
]

def classify_intent_with_gpt(user_input, client, user_memory=None):
    """
    Classify the user's intent based on their input using a GPT model.
    
    Args:
        user_input (str): The input text from the user.
        client: The GPT client to use for classification.
        user_memory (dict, optional): Memory of previous interactions with the user.
        
    Returns:
        str: The detected intent ('url', 'job_description', 'question', 'greeting', 'farewell', or 'other').
    """
    memory_context = ""
    if user_memory:
        memory_info = []
        for key, value in user_memory.items():
            if value:
                memory_info.append(f"{key}: {value}")
        if memory_info:
            memory_context = f"\n\nUser's stored information: {', '.join(memory_info)}"
    
    system_message = f"""
    You are an intent classifier for a career advice chatbot. Analyze the user's input and determine the most appropriate action.

    Guidelines:
    1. If it's a valid URL (http/https), use process_job_url
    2. If it's a long text that appears to be a job description, use process_job_description
    3. If it's a career-related question, use answer_career_question
    4. If the user is sharing personal information (name, role, experience, skills), use store_personal_info
    5. If it's completely off-topic (not about careers/resumes/jobs), use handle_off_topic
    
    The user input should be analyzed in context of career advice and resume assistance.{memory_context}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_input}
            ],
            functions=INTENT_FUNCTIONS,
            function_call="auto",
            temperature=0.1
        )
        
        # Check if a function was called
        if response.choices[0].message.function_call:
            function_name = response.choices[0].message.function_call.name
            function_args = eval(response.choices[0].message.function_call.arguments)
            
            return {
                'intent': function_name,
                'args': function_args,
                'type': 'function_call'
            }
        else:
            # Fallback to text response
            return {
                'intent': 'general_response',
                'message': response.choices[0].message.content,
                'type': 'text_response'
            }
            
    except Exception as e:
        print(f"Error in intent classification: {e}")
        # Fallback to simple classification
        return simple_fallback_classification(user_input)

def simple_fallback_classification(user_input):
    """
    A simple fallback classification for user input when GPT classification fails.
    
    Args:
        user_input (str): The input text from the user.
        
    Returns:
        str: The detected intent ('url', 'job_description', 'question', 'greeting', 'farewell', or 'other').
    """
    user_input_lower = user_input.strip().lower()
    
    if is_valid_url(user_input):
        return {
            'intent': 'process_job_url',
            'args': {'url': user_input},
            'type': 'function_call'
        }
    
    # Check for job description indicators
    job_desc_indicators = [
        'job description', 'position', 'responsibilities', 'requirements',
        'qualifications', 'skills required', 'we are looking for'
    ]
    
    indicator_count = sum(1 for indicator in job_desc_indicators if indicator in user_input_lower)
    if indicator_count >= 2 or len(user_input.split()) > 100:
        return {
            'intent': 'process_job_description',
            'args': {'job_description': user_input},
            'type': 'function_call'
        }
    
    # Check for off-topic queries
    off_topic_indicators = [
        'how to do pushups', 'exercise', 'cooking', 'recipe', 'weather',
        'sports', 'movies', 'music', 'travel', 'health', 'fitness'
    ]
    
    for indicator in off_topic_indicators:
        if indicator in user_input_lower:
            return {
                'intent': 'handle_off_topic',
                'args': {'off_topic_query': user_input},
                'type': 'function_call'
            }
    
    # Default to career question
    return {
        'intent': 'answer_career_question',
        'args': {'question': user_input},
        'type': 'function_call'
    }


def is_valid_url(url):
    """
    Check if the provided string is a valid URL.
    
    Args:
        url (str): The URL string to validate.
        
    Returns:
        bool: True if the URL is valid, False otherwise.
    """
    try:
        parsed = urlparse(url)
        return all([parsed.scheme in ('http', 'https'), parsed.netloc])
    except:
        return False
    
def get_system_prompt():
    """
    Get the system prompt for the resume advisor chatbot.
    
    Returns:
        str: The system prompt text.
    """
    return SYSTEM_PROMPT

def get_intent_functions():
    """
    Get the intent functions for the resume advisor chatbot.
    
    Returns:
        list: The list of intent functions.
    """
    return INTENT_FUNCTIONS