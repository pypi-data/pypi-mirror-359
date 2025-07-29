# ================================
# MAIN FUNCTION FOR CLI
# ================================

import argparse
import sys

from .core import AutoCommitAI, Config


def main():
    """Main function to handle command line arguments and execute the commit generation."""
    parser = argparse.ArgumentParser(
        description="Generate commit messages automatically using AI providers.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  %(prog)s                    # Generate a commit message for staged changes
  %(prog)s --all              # Include all files (staged and unstaged) in the commit
  %(prog)s --provider google  # Use Google Gemini
  %(prog)s --language es      # Generate commit message in Spanish (ISO 639-1)
    """,
    )

    parser.add_argument(
        "--provider",
        "-p",
        choices=["openai", "google", "azure"],
        help="AI provider to use for generating commit messages. Defaults to the provider set in the environment variable DEFAULT_AI_PROVIDER.",
    )

    parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="Add all files (staged and unstaged) to the commit. By default, only staged changes are included. All files will be added to the commit if this flag is set.",
    )

    parser.add_argument(
        "--language",
        "-l",
        default="en",  # Default to English if not specified
        help="Language for the generated commit message (e.g., 'en' for English, 'es' for Spanish), in format ISO 639-1. Defaults to 'en'.",
    )

    args = parser.parse_args()

    try:
        # Load configuration from environment variables
        config = Config.from_env()

        # Create and execute the AutoCommitGenerator
        generator = AutoCommitAI(config)
        generator.generate_and_commit(
            provider_name=args.provider, include_all=args.all, language=args.language
        )

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
