import json
from typing import TYPE_CHECKING, Optional

from .base import AIProvider

if TYPE_CHECKING:
    from ..config import Config


class GoogleProvider(AIProvider):
    """Gooogle Gemini provider"""

    def __init__(self, config: "Config"):
        super().__init__(config)
        try:
            from google import genai

            self.client = genai.Client(api_key=config.google_api_key)
            self.model = config.google_model
        except ImportError:
            raise ImportError(
                "Module 'google' is not installed. Please install it with 'pip install google-genai'."
            )

    def is_configured(self) -> bool:
        """Check if the provider is configured."""
        return bool(self.config.google_api_key)

    def generate_commit_message(
        self, diff_content: str, language: Optional[str] = None
    ) -> str:
        """Generate a commit message using Google Gemini."""
        language = language or self.config.default_lang or "en"
        prompt = (
            self.prompts.SYSTEM_PROMPT
            + "\n\n"
            + self._create_base_prompt(diff_content, language)
        )

        max_attempts = 3
        attemps = 0
        while attemps < max_attempts:
            try:
                response = self.client.models.generate_content(
                    model=self.model, contents=prompt
                )
                response_content = response.text.strip()
                return json.loads(self._clean_markdown_json_block(response_content))
            except Exception as e:
                # if "Expecting value: line 1 column 1 (char 0)" in str(e):
                #     print(
                #         f" Error generating commit message with Google Gemini. Probably the response is malformed."
                #     )
                # else:
                #     print(
                #         f"Error generating commit message with Google Gemini: {str(e)}"
                #     )
                #     print(f"Response content: {response}")
                # print("Retrying...")
                attemps += 1
        if attemps == max_attempts:
            raise Exception(
                f"Error generating commit message with Google Gemini after {max_attempts} attempts"
            )
