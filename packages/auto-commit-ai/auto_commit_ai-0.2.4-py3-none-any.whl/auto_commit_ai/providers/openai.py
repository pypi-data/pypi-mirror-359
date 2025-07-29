import json
from typing import TYPE_CHECKING, Optional

from .base import AIProvider

if TYPE_CHECKING:
    from ..config import Config


class OpenAIProvider(AIProvider):
    """OpenAI provider"""

    def __init__(self, config: "Config", custom_prompts_path: Optional[str] = None):
        super().__init__(config, custom_prompts_path)
        try:
            import openai

            self.client = openai.OpenAI(
                api_key=config.openai_api_key, base_url=config.openai_base_url
            )
        except ImportError:
            raise ImportError(
                "Module 'openai' is not installed. Please install it with 'pip install openai'."
            )

    def is_configured(self) -> bool:
        """Check if the provider is configured."""
        return bool(self.config.openai_api_key)

    def generate_commit_message(
        self, diff_content: str, language: Optional[str] = None
    ) -> str:
        """Generate a commit message using OpenAI."""
        language = language or self.config.default_lang or "en"
        prompt = self._create_base_prompt(diff_content, language)

        max_attempts = 3
        attemps = 0
        while attemps < max_attempts:
            try:
                response = self.client.chat.completions.create(
                    model=self.config.openai_model,
                    messages=[
                        {
                            "role": "system",
                            "content": self.prompts.SYSTEM_PROMPT,
                        },
                        {"role": "user", "content": prompt},
                    ],
                )
                response_content = response.choices[0].message.content.strip()
                # Parse the response content as JSON
                return json.loads(self._clean_markdown_json_block(response_content))
            except Exception as e:
                # if "Expecting value: line 1 column 1 (char 0)" in str(e):
                #     print(
                #         f" Error generating commit message with OpenAI. Probably the response is malformed."
                #     )
                # else:
                #     print(f"Error generating commit message with OpenAI: {str(e)}")
                #     print(f"Response content: {response}")
                # print("Retrying...")
                attemps += 1
        if attemps == max_attempts:
            raise Exception(
                f"Error generating commit message with OpenAI after {max_attempts} attempts"
            )
