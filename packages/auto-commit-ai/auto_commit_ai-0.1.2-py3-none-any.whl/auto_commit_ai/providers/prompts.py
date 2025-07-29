# System prompts
OPENAI_SYSTEM_PROMPT = """You are an expert in Git who creates concise and descriptive commit titles and descriptions following best practices."""
GOOGLE_SYSTEM_PROMPT = """You are an expert in Git who creates concise and descriptive commit titles and descriptions following best practices."""

# Base prompt
BASE_COMMIT_PROMPT = """Based on the following code changes, generate a concise and descriptive commit title and description.
The message should follow conventional commit format, and must be redacted in {language} (ISO 639-1). If there are more than one relevant change, 
condense them into the title. Relevant changes are those that affect the functionality of the code, such as bug fixes, new features, 
or significant refactoring, but not just minor changes like whitespace, formatting, or comments. If there are only one relevant change,
use it as the title and provide a detailed description in the message.

Changes:

{diff_content}

Generate only the commit title and message, without additional explanations, and return them as a JSON object."""
