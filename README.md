# AI-Powered Resume Assistant

An interactive CLI tool that helps with resume creation, job application optimization, and career advice using OpenAI's GPT models.

## Features

- **Interactive Chat Interface**: Natural conversation with streaming responses
- **Web Scraping**: Extracts job descriptions from URLs
- **AI Analysis**: Uses OpenAI GPT to analyze job requirements
- **Resume Generation**: Creates tailored resume sections based on job descriptions
- **Session Management**: Maintains conversation context with LangChain memory
- **User Information Storage**: Remembers your details for personalized advice
- **Intent Classification**: Intelligently understands what you're asking for

## Setup

1. Clone this repository:

   ```bash
   git clone <your-repo-url>
   cd <your-repo-name>
   ```

2. Install required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key:

   - Create a `.env` file in the project root
   - Add your OpenAI API key: `OPENAI_API_KEY=your-api-key-here`
   - Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)

## Usage

Run the interactive CLI:

```bash
python main.py
```

### Available Commands

- `/new-session` - Start completely fresh session
- `/session-info` - Show current session details
- `/clear-user` - Clear user info only
- `/clear-history` - Clear chat history only
- `/memory` - Show current memory state
- `/help` - Show commands again
- `exit/quit` - Exit the program

### Example Interactions

- Paste a job URL to get tailored resume sections
- Share your name, experience, and skills for personalized advice
- Ask career-related questions for expert guidance
- Submit job descriptions for analysis and resume optimization

## Requirements

- Python 3.7+
- OpenAI API key
- Internet connection for web scraping

## Security Note

Never commit your `.env` file to version control. It contains sensitive API keys.
