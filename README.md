# AI-Powered Resume Tailoring Tool

This Jupyter notebook automatically generates tailored resume sections based on job descriptions using OpenAI's API.

## Features

- **Web Scraping**: Extracts job descriptions from URLs
- **AI Analysis**: Uses OpenAI GPT to analyze job requirements
- **Resume Generation**: Creates tailored Objective, Qualifications, and Technical Skills sections
- **Markdown Output**: Clean, formatted output ready for use

## Setup

1. Clone this repository:

   ```bash
   git clone <your-repo-url>
   cd <your-repo-name>
   ```

2. Install required packages:

   ```bash
   pip install openai python-dotenv requests beautifulsoup4 ipython
   ```

3. Set up your OpenAI API key:

   - Copy `.env.example` to `.env`
   - Add your OpenAI API key to the `.env` file
   - Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)

4. Run the Jupyter notebook:
   ```bash
   jupyter notebook Tailored_resume.ipynb
   ```

## Usage

1. Replace the job URL in the notebook with your target job posting
2. Run all cells to generate tailored resume sections
3. Copy the generated markdown output to your resume

## Requirements

- Python 3.7+
- OpenAI API key
- Internet connection for web scraping

## Security Note

Never commit your `.env` file to version control. It contains sensitive API keys.
