# How to Use Aider

Aider is an AI-powered coding assistant that helps you edit code in your local repository using natural language commands. Here's how to get started:

## Installation

```bash
pip install aider-chat
```

## Basic Usage

1. Navigate to your project directory:
   ```bash
   cd your-project-directory
   ```

2. Start Aider:
   ```bash
   aider
   ```

3. Or specify files to work with:
   ```bash
   aider tailored_resume_chatbot.py
   ```

## Common Commands

- **Edit code**: Simply describe the changes you want to make in natural language
- **Add files**: `add filename.py` to include more files in the current session
- **Commit changes**: `/commit "Your commit message"` to commit changes to git
- **Help**: `/help` to see all available commands
- **Quit**: `/quit` to exit Aider

## Tips for Effective Use

1. Be specific about what you want to change
2. Start with small, focused changes
3. Review changes before committing
4. Use `/diff` to see what changes Aider is proposing
5. Use `/undo` if you need to revert changes

## Example Workflow

1. Start Aider with your main file:
   ```bash
   aider tailored_resume_chatbot.py
   ```

2. Ask for a specific change:
   ```
   Add error handling for network timeouts when fetching job descriptions
   ```

3. Review the proposed changes
4. Commit when satisfied:
   ```
   /commit "Add network timeout error handling"
   ```

5. Continue with more changes or quit:
   ```
   /quit
   ```

For more information, visit the [Aider documentation](https://aider.chat/docs/).
