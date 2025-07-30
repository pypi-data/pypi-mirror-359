SYSTEM_PROMPT = """You are an expert in Git who creates concise and descriptive commit titles and descriptions following 
best practices."""

BASE_COMMIT_PROMPT = """
Based on the following code changes, generate a concise and descriptive commit title and description. Adittionally, there are 
some extra information can be added:
- Branch name: to help you understand the general context of the changes. Usually is the name of an issue (not use only for 
the title, just use the name or key words to understand all the changes and know what is the purpose or objective of them)
- Previous commits: as branch name, it's only to have related changes made before, but you must to use the current changes mainly
- Additional context: specify requirements, objectives or extra info in case that it's not easy to extract only with the code

Requirements:
- Follow the Conventional Commits format.
- The message must be written in {language} (ISO 639-1).
- If there are multiple relevant changes (i.e., those that affect functionality such as bug fixes, features, or significant 
refactors), condense them into the title.
- If there's only one relevant change, use it as the title and provide a detailed description.
- Ignore irrelevant changes like formatting, whitespace, or comments.
- You must focus on the main changes and their purpose, not on the implementation details or minor changes (unless there are only minor changes).

Output instructions:
- Respond **only** with a JSON object containing exactly two keys: "title" and "description".
- Do **not** include any other text, explanation, or formatting outside of the JSON object.
- The response **must** be a valid JSON object. No markdown formatting. No introductory or closing remarks.

Return only the JSON object.

Following are all the information you have about the changes:

"""

BRANCH_NAME = """

Branch name:
{branch_name}

"""

PREVIOUS_COMMITS = """

Previous commits:
{previous_commits}

"""

ADDITIONAL_CONTEXT = """

Additional context:
{additional_context}

"""

CODE_CHANGES = """

Code changes:
{diff_content}

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
