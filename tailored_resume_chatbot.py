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

def chat_about_resumes(query):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=message_for(query, is_website=False),
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
            if intent_info['intent'] == 'process_job_url':
                summary = generate_resume_sections(intent_info['args']['url'])
                return summary
                
            elif intent_info['intent'] == 'process_job_description':
                result = process_job_description(intent_info['args']['job_description'])
                return result
                
            elif intent_info['intent'] == 'answer_career_question':
                response = chat_about_resumes(intent_info['args']['question'])
                return response
                
            elif intent_info['intent'] == 'store_personal_info':
                # Store the personal information for future personalization
                info_type = intent_info['args']['info_type']
                info_value = intent_info['args']['info_value']
                user_memory[info_type] = info_value
                return f"Personal information stored: {info_type}"
                
            elif intent_info['intent'] == 'handle_off_topic':
                return "I'm specialized in helping with resumes, job applications, and career advice."
                
            else:
                # Handle general responses or fallbacks
                if 'message' in intent_info:
                    return intent_info['message']
                else:
                    return "I'm not sure I understood that. Could you please rephrase?"
                
        except Exception as e:
            error_msg = f"An error occurred: {e}"
            return error_msg
        
    
if __name__ == "__main__":
    main()
