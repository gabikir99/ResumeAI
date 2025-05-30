import os
import requests
import time
import sys
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from IPython.display import Markdown, display
from openai import OpenAI
from urllib.parse import urlparse
from user_intent import classify_intent_with_gpt, simple_fallback_classification, get_system_prompt, get_intent_functions, is_valid_url

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    )
}

class Website:

    def __init__(self, url):
        self.url = url
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        self.title = soup.title.string if soup.title else "No title found"
        for tag in soup.body(["script", "style", "img", "input"]):
            tag.decompose()
        self.text = soup.body.get_text(separator='\n', strip=True)

    def user_prompt(self):
        return (
            f"You're looking at the job description website titled '{self.title}'.\n\n"
            f"Here’s the job description:\n\n{self.text}"
        )
        
def message_for(content, is_website=True):
    system_prompt = get_system_prompt()

    if is_website:
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content.user_prompt()},
        ]
    else:
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content},
        ]

def print_streaming(text):
    """Print text character by character with a slight delay to simulate typing."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.01)  # Adjust delay as needed

def generate_resume_sections(url):
    website = Website(url)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=message_for(website, is_website=True),
        max_tokens=1500,
        temperature=0.3,
        stream=True
    )
    
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            print_streaming(content)
            full_response += content
    
    return full_response

def chat_about_resumes(query, user_memory=None):
    # Create messages with user memory context if available
    messages = message_for(query, is_website=False)
    
    # Add user memory context if available
    if user_memory and len(user_memory) > 0:
        memory_context = "User information: "
        memory_items = []
        for key, value in user_memory.items():
            memory_items.append(f"{key}: {value}")
        
        memory_context += ", ".join(memory_items)
        memory_context += "\n\nIf the user asks about their personal information (like 'what is my name?', 'what experience do I have?', etc.), respond with the stored information in a natural way."
        
        # Insert memory context as a system message before the user query
        messages.insert(1, {"role": "system", "content": memory_context})
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=1500,
        temperature=0.7,
        stream=True
    )
    
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            print_streaming(content)
            full_response += content
    
    return full_response

def process_job_description(text):
    """Process a job description directly from text."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=message_for(text, is_website=False),
        max_tokens=1500,
        temperature=0.3,
        stream=True
    )
    
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            print_streaming(content)
            full_response += content
    
    return full_response

def handle_greeting(greeting, user_memory=None):
    """Handle user greetings with personalized responses."""
    greeting_responses = [
        "Hello! How can I help with your resume or job search today?",
        "Hi there! Ready to work on your career development?",
        "Greetings! What career assistance do you need today?",
        "Welcome! How can I help with your professional development?"
    ]
    
    # Personalize greeting if we know the user's name
    if user_memory and 'name' in user_memory:
        personalized_responses = [
            f"Hello {user_memory['name']}! How can I help with your resume or job search today?",
            f"Hi {user_memory['name']}! Ready to work on your career development?",
            f"Greetings {user_memory['name']}! What career assistance do you need today?",
            f"Welcome back {user_memory['name']}! How can I help with your professional development?"
        ]
        greeting_responses = personalized_responses
    
    # Select a response (could be randomized in a more sophisticated implementation)
    response = greeting_responses[0]
    print_streaming(response)
    return response

def handle_goodbye(farewell, user_memory=None):
    """Handle user farewells with personalized responses."""
    farewell_responses = [
        "Goodbye! Feel free to return when you need more help with your career.",
        "Take care! I'm here when you need resume or job search assistance.",
        "Until next time! Best of luck with your career journey.",
        "Farewell! Come back anytime for more career advice."
    ]
    
    # Personalize farewell if we know the user's name
    if user_memory and 'name' in user_memory:
        personalized_responses = [
            f"Goodbye {user_memory['name']}! Feel free to return when you need more help with your career.",
            f"Take care {user_memory['name']}! I'm here when you need resume or job search assistance.",
            f"Until next time {user_memory['name']}! Best of luck with your career journey.",
            f"Farewell {user_memory['name']}! Come back anytime for more career advice."
        ]
        farewell_responses = personalized_responses
    
    # Select a response (could be randomized in a more sophisticated implementation)
    response = farewell_responses[0]
    print_streaming(response)
    return response

def main():
    # Initialize user memory for personalization
    user_memory = {}
    
    while True:
        user_input = input("What can I help you with today? \n").strip()
        
        if user_input.lower() in ['exit', 'quit']:
            break
        
        try:
            # Classify the user's intent using GPT
            intent_info = classify_intent_with_gpt(user_input, client, user_memory)
            
            # If GPT classification fails, fall back to simple classification
            if not intent_info:
                intent_info = simple_fallback_classification(user_input)
            
            # Handle the intent based on the classification
            if intent_info['intent'] == 'handle_greeting':
                handle_greeting(intent_info['args']['greeting'], user_memory)
                
            elif intent_info['intent'] == 'handle_goodbye':
                handle_goodbye(intent_info['args']['farewell'], user_memory)
                # If the user is saying goodbye, we could optionally break the loop here
                # if you want the chatbot to end the conversation
                # break
                
            elif intent_info['intent'] == 'process_job_url':
                summary = generate_resume_sections(intent_info['args']['url'])
                
            elif intent_info['intent'] == 'process_job_description':
                result = process_job_description(intent_info['args']['job_description'])
                
            elif intent_info['intent'] == 'answer_career_question':
                response = chat_about_resumes(intent_info['args']['question'], user_memory)
                
            elif intent_info['intent'] == 'store_personal_info':
                # Store the personal information for future personalization
                info_type = intent_info['args']['info_type']
                info_value = intent_info['args']['info_value']
                user_memory[info_type] = info_value
                
                # Instead of showing a storage message, respond naturally
                response = chat_about_resumes(f"I've noted that your {info_type} is {info_value}. How can I help with your resume or career questions?", user_memory)
                
            elif intent_info['intent'] == 'handle_off_topic':
                print_streaming("I'm specialized in helping with resumes, job applications, and career advice.")
                
            else:
                # Handle general responses or fallbacks
                if 'message' in intent_info:
                    print_streaming(intent_info['message'])
                else:
                    print_streaming("I'm not sure I understood that. Could you please rephrase?")
                
        except Exception as e:
            error_msg = f"An error occurred: {e}"
            print_streaming(error_msg)
        
    
if __name__ == "__main__":
    main()
