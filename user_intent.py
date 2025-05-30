import re
from urllib.parse import urlparse

# System prompt for the resume advisor chatbot
SYSTEM_PROMPT = """
You are a friendly and professional career advisor chatbot specializing in resumes and job applications.

When a user provides a job description, help them by generating:

1. An Objective — a brief 1–2 sentence summary of why they are a great fit for the role.

2. A list of exactly 6-7 Highlights of Qualifications — specific, relevant points about their skills, achievements, or experience that match the job.

3. A categorized list of Technical Skills — do not list them as a single list. Instead, group them under headings such as:
- Programming Languages, IDEs, and Libraries
- Data Tools
- Machine Learning & AI Tools
- Cloud Platforms
- DevOps & Version Control
- Other Tools or Techniques

Use only the categories relevant to the job. List the tools in each group separated by commas.

IMPORTANT: Do not use any Markdown formatting in your responses. Do not use asterisks (*) around section titles or for emphasis. Do not use backticks (`) for code. Do not use any special formatting characters. Present all text as plain text only.

For general questions about resumes, job applications, interviews, or career advice, provide helpful, concise, and practical guidance.
"""

def classify_intent(user_input):
    """
    Classify the user's intent based on their input.
    
    Returns:
        str: One of 'url', 'job_description', 'question', 'greeting', 'farewell', or 'other'
    """
    user_input = user_input.strip().lower()
    
    # Check if it's a URL
    if is_valid_url(user_input):
        return 'url'
    
    # Check if it's a farewell
    farewell_patterns = [
        r'\b(bye|goodbye|exit|quit|end|stop|farewell)\b',
        r'thank.*you.*bye',
        r'see you later',
        r'i\'m done',
        r'that\'s all'
    ]
    for pattern in farewell_patterns:
        if re.search(pattern, user_input):
            return 'farewell'
    
    # Check if it's a greeting
    greeting_patterns = [
        r'\b(hi|hello|hey|greetings|howdy)\b',
        r'good (morning|afternoon|evening)',
        r'nice to (meet|see) you',
        r'how are you'
    ]
    for pattern in greeting_patterns:
        if re.search(pattern, user_input):
            return 'greeting'
    
    # Check if it's a job description
    job_desc_indicators = [
        'job description', 'position', 'responsibilities', 'requirements',
        'qualifications', 'skills required', 'experience required',
        'we are looking for', 'we are hiring', 'job title', 'job summary',
        'about the role', 'about this position', 'job details'
    ]
    
    # Count how many job description indicators are present
    indicator_count = sum(1 for indicator in job_desc_indicators if indicator in user_input)
    if indicator_count >= 2 or len(user_input.split()) > 100:  # If text is long or has multiple indicators
        return 'job_description'
    
    # If none of the above, assume it's a question
    question_indicators = ['?', 'how', 'what', 'why', 'when', 'where', 'who', 'which', 'can you', 'could you', 'help me']
    for indicator in question_indicators:
        if indicator in user_input:
            return 'question'
    
    # Default to 'other' if we can't determine the intent
    return 'other'

def is_valid_url(url):
    """Check if the input is a valid URL."""
    try:
        parsed = urlparse(url)
        return all([parsed.scheme in ("http", "https"), parsed.netloc])
    except:
        return False

def get_response_for_intent(intent, user_input):
    """
    Generate an appropriate response based on the detected intent.
    This function doesn't actually generate the response but returns
    information about how to handle the intent.
    
    Returns:
        dict: Contains information about how to handle the intent
    """
    if intent == 'url':
        return {
            'type': 'url',
            'message': "I'll analyze this job posting for you.",
            'action': 'process_url',
            'data': user_input
        }
    
    elif intent == 'job_description':
        return {
            'type': 'job_description',
            'message': "I'll analyze this job description for you.",
            'action': 'process_job_description',
            'data': user_input
        }
    
    elif intent == 'question':
        return {
            'type': 'question',
            'message': "Let me answer that for you.",
            'action': 'answer_question',
            'data': user_input
        }
    
    elif intent == 'greeting':
        return {
            'type': 'greeting',
            'message': "Hello! I'm your resume tailoring assistant. You can share a job description URL or ask me questions about resumes and job applications.",
            'action': 'simple_response',
            'data': None
        }
    
    elif intent == 'farewell':
        return {
            'type': 'farewell',
            'message': "Goodbye! Feel free to come back anytime you need help with your resume or job applications.",
            'action': 'exit',
            'data': None
        }
    
    else:  # 'other'
        return {
            'type': 'other',
            'message': "I'm not sure what you're asking. You can share a job posting URL, paste a job description, or ask me questions about resumes and job applications.",
            'action': 'simple_response',
            'data': None
        }

def get_system_prompt():
    """Return the system prompt for the chatbot."""
    return SYSTEM_PROMPT
