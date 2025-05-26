import os
import requests
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
        
def message_for(website):
    system_prompt = """
    You are a friendly and professional career advisor chatbot.

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
"""


    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": website.user_prompt()},
    ]

def generate_resume_sections(url):
    website = Website(url)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=message_for(website),
        max_tokens=1500,
        temperature=0.3
    )
    return "\n" + response.choices[0].message.content.strip()

def is_valid_url(url):
    try:
        parsed = urlparse(url)
        return all([parsed.scheme in ("http", "https"), parsed.netloc])
    except:
        return False


def main():
    print("\nWelcome to the Tailored Resume Chatbot!\n")
    print("Type 'exit' or 'quit' at any time to stop.\n")
    
    while True:
        url = input("Please enter the job description URL: \n").strip()
        
        if url.lower() in ['exit', 'quit']:
            print("Exiting the chatbot. Goodbye!")
            break
            
        if is_valid_url(url):
            try:
                print("Processing job description... Please wait.\n")
                summary = generate_resume_sections(url)
                print(summary)
                print("\n" + "="*50 + "\n") 
                print("You can enter another URL or type 'exit'/'quit' to stop.\n")
            except Exception as e:
                print(f"An error occurred while processing the URL: {e}")
                print("Please try again with a different URL.\n")
        else:
            print("That doesn't look like a valid URL. Please include http:// or https:// and a valid domain.\n")
        
    
if __name__ == "__main__":
    main()
