import importlib.util
import json
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

from . import prompts

if TYPE_CHECKING:
    from ..config import Config


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    def __init__(
        self, config: "Config", custom_prompts_path: Optional[Union[str, Path]] = None
    ):
        self.config = config
        self.prompts = self._load_prompts(custom_prompts_path)

    def _load_prompts(self, custom_prompts_path: Optional[Union[str, Path]] = None):
        """Load prompts from custom path or default module."""
        # custom_prompts_path = (
        #     custom_prompts_path
        #     if custom_prompts_path
        #     else self.config.custom_prompts_path
        # )
        if custom_prompts_path is None:
            return prompts

        # Convert to Path object if string
        prompts_path = Path(custom_prompts_path)

        if not prompts_path.exists():
            raise FileNotFoundError(f"Custom prompts file not found: {prompts_path}")

        # Load the custom prompts module
        spec = importlib.util.spec_from_file_location("custom_prompts", prompts_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load prompts from: {prompts_path}")

        custom_prompts = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(custom_prompts)

        print(f"🔍 Loaded custom prompts from: {prompts_path}")
        return custom_prompts

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
