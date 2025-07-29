from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

from .azure import AzureOpenAIProvider
from .base import AIProvider
from .google import GoogleProvider
from .ollama import OllamaProvider
from .openai import OpenAIProvider

if TYPE_CHECKING:
    from ..config import Config


class AIProviderFactory:
    """Factory to create AI providers."""

    @staticmethod
    def create_provider(
        provider_name: str,
        config: "Config",
        custom_prompts_path: Optional[Union[str, Path]] = None,
    ) -> AIProvider:
        """Creaate an AI provider based on the provider name and configuration."""
        providers = {
            "openai": OpenAIProvider,
            "google": GoogleProvider,
            "azure": AzureOpenAIProvider,
            "ollama": OllamaProvider,
        }

        if provider_name not in providers:
            available = ", ".join(providers.keys())
            raise ValueError(
                f"Provider '{provider_name}' not available. Available: {available}"
            )

        provider = providers[provider_name](config, custom_prompts_path)

        if not provider.is_configured():
            raise ValueError(
                f"Provider '{provider_name}' is not configured correctly. "
                f"Check your configuration settings."
            )
        return provider

    @staticmethod
    def get_available_providers() -> list[str]:
        """Returns a list of available AI providers."""
        return ["openai", "google", "azure", "ollama"]

    @staticmethod
    def is_provider_available(provider_name: str) -> bool:
        """Check if a provider is available."""
        return provider_name in AIProviderFactory.get_available_providers()
