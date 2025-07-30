"""Auto Commit AI - Generate commit messages automatically using AI providers."""

__author__ = "Toni Miquel Llull"

from .config import Config
from .core import AutoCommitAI
from .providers.factory import AIProviderFactory

__all__ = ["AutoCommitAI", "AIProviderFactory", "Config"]
