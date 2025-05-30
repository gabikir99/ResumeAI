import os
import requests
import time
import sys
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from IPython.display import Markdown, display
from openai import OpenAI
from urllib.parse import urlparse
from user_intent import classify_intent, get_response_for_intent, get_system_prompt

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
    
    while True:
        user_input = input("What can I help you with today? \n").strip()
        
        # Classify the user's intent
        intent = classify_intent(user_input)
        response_info = get_response_for_intent(intent, user_input)
        
        # Handle the intent
        if response_info['type'] == 'farewell' or user_input.lower() in ['exit', 'quit']:
            print_streaming(response_info['message'])
            print("\n")
            break
            
        elif response_info['type'] == 'greeting' or response_info['type'] == 'other':
            print_streaming(response_info['message'])
            print("\n")
            
        elif response_info['type'] == 'url':
            try:
                print_streaming(response_info['message'])
                print("\n")
                summary = generate_resume_sections(user_input)
            except Exception as e:
                error_msg = f"An error occurred while processing the URL: {e}"
                print_streaming(error_msg)
                print("\n")
                print_streaming("Please try again with a different URL.")
                print("\n")
                
        elif response_info['type'] == 'job_description':
            try:
                process_job_description(user_input)
            except Exception as e:
                error_msg = f"An error occurred while processing the job description: {e}"
                print_streaming(error_msg)
                print("\n")
                print_streaming("Please try again with a different description.")
                print("\n")
                
        elif response_info['type'] == 'question':
            try:
                print_streaming(response_info['message'])
                print("\n")
                response = chat_about_resumes(user_input)
            except Exception as e:
                error_msg = f"An error occurred while processing your question: {e}"
                print_streaming(error_msg)
                print("\n")
                print_streaming("Please try asking in a different way.")
                print("\n")
        
        print("\n" + "="*50 + "\n")
        print_streaming("You can enter another URL, paste a job description, ask another question, or type 'exit'/'quit' to stop.")
        print("\n")
        
    
if __name__ == "__main__":
    main()
