import sys
import time
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

def print_streaming(text):
    """Print text character by character with a slight delay to simulate typing."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.01)  # Adjust delay as needed

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

class Website:
    """Class to handle website scraping and text extraction."""
    
    def __init__(self, url):
        self.url = url
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        self.title = soup.title.string if soup.title else "No title found"
        for tag in soup.body(["script", "style", "img", "input"]):
            tag.decompose()
        self.text = soup.body.get_text(separator='\n', strip=True)

    def user_prompt(self):
        return (
            f"You're looking at the job description website titled '{self.title}'.\n\n"
            f"Here's the job description:\n\n{self.text}"
        )
