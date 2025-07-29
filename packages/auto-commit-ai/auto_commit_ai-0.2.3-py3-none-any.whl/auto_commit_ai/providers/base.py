import json
import re
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from . import prompts

if TYPE_CHECKING:
    from ..config import Config


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    def __init__(self, config: "Config"):
        self.config = config
        self.prompts = prompts

    @abstractmethod
    def generate_commit_message(
        self, diff_content: str, language: Optional[str] = None
    ) -> json:
        """Generate a commit message based on the provided diff content."""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if the provider is configured."""
        pass

    def _create_base_prompt(
        self, diff_content: str, language: Optional[str] = None
    ) -> str:
        """Create the base prompt for generating commit messages."""
        language = language or self.config.default_lang or "en"
        return (
            prompts.BASE_COMMIT_PROMPT.format(
                diff_content=diff_content, language=language
            )
            # + self.prompts.RESPONSE_JSON_EXAMPLE
        )

    def _clean_markdown_json_block(self, content: str) -> str:
        """Remove markdown code blocks and extract JSON content."""
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
        if match:
            return match.group(1)
        return content.strip()
