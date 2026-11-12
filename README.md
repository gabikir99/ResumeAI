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

3. Set environment variables. The app reads secrets from the environment and will not start the database layer without `DATABASE_URL`.

   ```bash
   cp .env.example .env
   cp frontend/.env.example frontend/.env
   ```

   Fill in `.env` (project root, loaded by Python) and `frontend/.env` (loaded by Create React App). Placeholder names are listed in those example files. Do not commit either `.env` file.

   **Local Python (root `.env`)**

   | Variable | When it is needed |
   | --- | --- |
   | `DATABASE_URL` | Always. PostgreSQL URL, for example `postgresql://USER:PASSWORD@localhost:5432/resume_assistant`. Startup fails with a clear error if this is missing. |
   | `OPENAI_API_KEY` | Chat and CLI. Create a key at [OpenAI Platform](https://platform.openai.com/api-keys). |
   | `GOOGLE_CLIENT_ID` | Google sign-in. OAuth **client ID** only (the API uses it to verify tokens). |
   | `ADMIN_KEY` | Admin routes `/api/rate-limit/reset` and `/api/admin/sessions`. Those routes return an error if this is unset. |
   | `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `ADMIN_EMAIL` | `POST /api/feedback` only. `SMTP_PORT` defaults to `587`. |
   | `SQL_ECHO` | Optional. Set to `true` to log SQL. |

   **Local React (`frontend/.env`)**

   | Variable | When it is needed |
   | --- | --- |
   | `REACT_APP_API_URL` | Optional. Flask base URL. Defaults to `http://localhost:5000`. |
   | `REACT_APP_GOOGLE_CLIENT_ID` | Google sign-in button. Same client ID as `GOOGLE_CLIENT_ID`. |

   Restart `python app.py` / `npm start` after changing these files. Create React App only exposes variables that start with `REACT_APP_`, and it reads them at dev-server or build time.

### Render

Set the same variables in the Render dashboard. Do not put real values in the repo.

- **Flask web service:** open the service, then **Environment**, and add `OPENAI_API_KEY`, `GOOGLE_CLIENT_ID`, `ADMIN_KEY`, and the SMTP variables if you use feedback email. For Postgres, create a Render PostgreSQL database and attach it to this service so Render injects `DATABASE_URL` (use that internal URL). If you set `DATABASE_URL` yourself, paste it only in the dashboard. The process exits on boot if `DATABASE_URL` is missing.
- **React static site or web service:** set `REACT_APP_API_URL` to the public Flask URL and `REACT_APP_GOOGLE_CLIENT_ID` to the same Google client ID. Create React App bakes `REACT_APP_*` values in at **build** time, so change them and trigger a new deploy when they change. `GOOGLE_CLIENT_ID` on the API must match `REACT_APP_GOOGLE_CLIENT_ID`.

## Usage

### Command Line

Run the interactive CLI:

```bash
python main.py
```

### Web App

You can also use the provided React front‑end which talks to `app.py`.

1. Start the Flask API:

   ```bash
   python app.py
   ```

2. In another terminal start the React dev server:

   ```bash
   cd frontend
   npm install
   npm start
   ```

The React app will send requests to `/api/*` endpoints served by Flask.

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

Never commit `.env` or `frontend/.env`. They hold the database URL, API keys, and other secrets. `.env.example` and `frontend/.env.example` are safe to commit because they contain placeholders only. If a real credential was ever committed, rotate it in the provider (Postgres, OpenAI, Google, SMTP, admin key). Deleting it from the latest files does not remove it from older git commits.
