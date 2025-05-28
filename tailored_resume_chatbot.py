import os
import requests
import time
import sys
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from IPython.display import Markdown, display
from openai import OpenAI
from urllib.parse import urlparse

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
    system_prompt = """
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

    Use only the categories relevant to the job. List the tools in each group separated by commas. Do not use Markdown formatting — just plain text.

    For general questions about resumes, job applications, interviews, or career advice, provide helpful, concise, and practical guidance.
    """

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

def is_valid_url(url):
    try:
        parsed = urlparse(url)
        return all([parsed.scheme in ("http", "https"), parsed.netloc])
    except:
        return False


def main():
    print("\nWelcome to the Tailored Resume Chatbot!\n")
    print("You can:")
    print("1. Enter a job description URL to get tailored resume sections")
    print("2. Ask any question about resumes, job applications, or career advice")
    print("Type 'exit' or 'quit' at any time to stop.\n")
    
    while True:
        user_input = input("Enter a URL or ask a question: \n").strip()
        
        if user_input.lower() in ['exit', 'quit']:
            print("Exiting the chatbot. Goodbye!")
            break
            
        if is_valid_url(user_input):
            try:
                print("Processing job description... Please wait.\n")
                summary = generate_resume_sections(user_input)
                # No need to print summary as it's already printed in the streaming function
            except Exception as e:
                print(f"An error occurred while processing the URL: {e}")
                print("Please try again with a different URL.\n")
        else:
            try:
                print("Thinking about your question... Please wait.\n")
                response = chat_about_resumes(user_input)
                # No need to print response as it's already printed in the streaming function
            except Exception as e:
                print(f"An error occurred while processing your question: {e}")
                print("Please try asking in a different way.\n")
        
        print("\n" + "="*50 + "\n")
        print("You can enter another URL, ask another question, or type 'exit'/'quit' to stop.\n")
        
    
if __name__ == "__main__":
    main()
