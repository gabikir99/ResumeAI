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
    
    print("")  # Add a newline before starting
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            print_streaming(content)
            full_response += content
    print("")  # Add a newline at the end
    print("")  # Add a newline at the end
    
    return full_response

def chat_about_resumes(query):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=message_for(query, is_website=False),
        max_tokens=1500,
        temperature=0.7,
        stream=True
    )
    
    print("")  # Add a newline before starting
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            print_streaming(content)
            full_response += content
    
    return full_response

def process_job_description(text):
    """Process a job description directly from text."""
    print("Analyzing this job description... Please wait.\n")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=message_for(text, is_website=False),
        max_tokens=1500,
        temperature=0.3,
        stream=True
    )
    
    print("")  # Add a newline before starting
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            print_streaming(content)
            full_response += content
    print("")  # Add a newline at the end
    print("")  # Add a newline at the end
    
    return full_response

def main():
    print("\n")
    print_streaming("Welcome to the Tailored Resume Chatbot!")
    print("\n\n")
    print_streaming("You can:")
    print("\n")
    print_streaming("1. Enter a job description URL to get tailored resume sections")
    print("\n")
    print_streaming("2. Paste a job description directly")
    print("\n")
    print_streaming("3. Ask any question about resumes, job applications, or career advice")
    print("\n")
    print_streaming("Type 'exit' or 'quit' at any time to stop.")
    print("\n")
    
    # Initialize user memory for personalization
    user_memory = {}
    
    while True:
        user_input = input("What can I help you with today? \n").strip()
        
        if user_input.lower() in ['exit', 'quit']:
            print_streaming("Thank you for using the Tailored Resume Chatbot. Good luck with your job search!")
            print("\n")
            break
        
        try:
            # Classify the user's intent using GPT
            intent_info = classify_intent_with_gpt(user_input, client, user_memory)
            
            # If GPT classification fails, fall back to simple classification
            if not intent_info:
                intent_info = simple_fallback_classification(user_input)
            
            # Handle the intent based on the classification
            if intent_info['intent'] == 'process_job_url':
                print_streaming("Analyzing this job posting URL... Please wait.\n")
                summary = generate_resume_sections(intent_info['args']['url'])
                
            elif intent_info['intent'] == 'process_job_description':
                print_streaming("Analyzing this job description... Please wait.\n")
                process_job_description(intent_info['args']['job_description'])
                
            elif intent_info['intent'] == 'answer_career_question':
                print_streaming("Let me help you with that career question...\n")
                response = chat_about_resumes(intent_info['args']['question'])
                
            elif intent_info['intent'] == 'store_personal_info':
                # Store the personal information for future personalization
                info_type = intent_info['args']['info_type']
                info_value = intent_info['args']['info_value']
                user_memory[info_type] = info_value
                
                print_streaming(f"Thanks for sharing your {info_type}. I'll remember that to provide more personalized advice.\n")
                
            elif intent_info['intent'] == 'handle_off_topic':
                print_streaming("I'm specialized in helping with resumes, job applications, and career advice. Could you please ask me something related to those topics?\n")
                
            else:
                # Handle general responses or fallbacks
                if 'message' in intent_info:
                    print_streaming(intent_info['message'])
                else:
                    print_streaming("I'm not sure I understood that. Could you please rephrase or ask me about resumes, job applications, or career advice?")
                print("\n")
                
        except Exception as e:
            error_msg = f"An error occurred: {e}"
            print_streaming(error_msg)
            print("\n")
            print_streaming("Please try again with a different query.")
            print("\n")
        
        print("\n" + "="*50 + "\n")
        print_streaming("You can enter another URL, paste a job description, ask another question, or type 'exit'/'quit' to stop.")
        print("\n")
        
    
if __name__ == "__main__":
    main()
