# System prompts
SYSTEM_PROMPT = """You are an expert in Git who creates concise and descriptive commit titles and descriptions following best practices."""

BASE_COMMIT_PROMPT = """
Based on the following code changes, generate a concise and descriptive commit title and description.

Requirements:
- Follow the Conventional Commits format.
- The message must be written in {language} (ISO 639-1).
- If there are multiple relevant changes (i.e., those that affect functionality such as bug fixes, features, or significant refactors), condense them into the title.
- If there's only one relevant change, use it as the title and provide a detailed description.
- Ignore irrelevant changes like formatting, whitespace, or comments.

Output instructions:
- Respond **only** with a JSON object containing exactly two keys: "title" and "description".
- Do **not** include any other text, explanation, or formatting outside of the JSON object.
- The response **must** be a valid JSON object. No markdown formatting. No introductory or closing remarks.

Code changes:
{diff_content}

Return only the JSON object.

"""

RESPONSE_JSON_EXAMPLE = """
RESPONSE JSON EXAMPLE:
```json
{
    "title": "feat: add new feature",
    "description": "This commit adds a new feature that improves the user experience by allowing users to customize their settings."
}
```

"""
