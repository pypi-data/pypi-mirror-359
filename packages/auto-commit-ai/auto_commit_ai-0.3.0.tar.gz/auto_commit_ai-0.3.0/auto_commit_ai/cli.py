# ================================
# MAIN FUNCTION FOR CLI
# ================================

import argparse
import sys
from pathlib import Path

from .core import AutoCommitAI, Config


def setup_parser() -> argparse.ArgumentParser:
    """Setup and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="🤖 Generate commit messages automatically using AI providers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🚀 Some examples:
  %(prog)s                           # Generate commit for staged changes
  %(prog)s --all                     # Include all files (staged + unstaged + untracked)
  %(prog)s --provider google         # Use Google Gemini
  %(prog)s --language es             # Generate in Spanish
  %(prog)s --preview                 # Preview message without committing
  %(prog)s --stage                   # Interactive file staging
  %(prog)s --custom-prompts ./my_prompts.py  # Use custom prompts file
  %(prog)s -ac                       # Additional context for commit message
  %(prog)s --branch-name             # Use current branch name in commit context

🔧 Providers: openai, google, azure, ollama
🌍 Languages: en, es, fr, de, it, pt, ja, zh, ru, etc. (ISO 639-1)
    """,
    )

    # Main functionality arguments
    parser.add_argument(
        "--provider",
        "-p",
        choices=["openai", "google", "azure", "ollama"],
        help="AI provider to use for generating commit messages",
    )

    parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="Include all files (staged + unstaged + untracked) in the commit",
    )

    parser.add_argument(
        "--language",
        "-l",
        type=str,
        help="Language for commit message (ISO 639-1 format, e.g., 'en', 'es', 'fr')",
    )

    parser.add_argument(
        "--repo",
        "-r",
        type=str,
        default=".",
        help="Path to Git repository (defaults to current directory)",
    )

    # Action arguments (mutually exclusive)
    action_group = parser.add_mutually_exclusive_group()

    action_group.add_argument(
        "--preview",
        action="store_true",
        help="Generate and preview commit message without committing",
    )

    action_group.add_argument(
        "--status", action="store_true", help="Show detailed repository status"
    )

    action_group.add_argument(
        "--stage",
        action="store_true",
        help="Interactive staging of files before committing",
    )

    action_group.add_argument(
        "--history", action="store_true", help="Show recent commit history"
    )

    parser.add_argument(
        "--no-status",
        action="store_true",
        help="Don't show repository status before generating commit",
    )

    parser.add_argument(
        "--custom-prompts",
        "-c",
        type=str,
        help="Path to custom prompts file (Python module with prompts configuration)",
    )

    parser.add_argument(
        "--branch-name",
        "-bn",
        action="store_true",
        help="Use current branch name in commit context (default: False)",
    )

    parser.add_argument(
        "--previous-commits",
        "-pc",
        action="store_true",
        help="Use previous commits as context for commit message generation (default: False)",
    )

    parser.add_argument(
        "--additional-context",
        "-ac",
        type=str,
        help="Additional context to include in commit message generation",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    return parser


def validate_repository_path(repo_path: str) -> Path:
    """Validate and return the repository path."""
    path = Path(repo_path).resolve()

    if not path.exists():
        raise ValueError(f"Repository path does not exist: {repo_path}")

    if not path.is_dir():
        raise ValueError(f"Repository path is not a directory: {repo_path}")

    return path


def validate_custom_prompts_path(prompts_path: str) -> Path:
    """Validate and return the custom prompts path."""
    path = Path(prompts_path).resolve()

    if not path.exists():
        raise ValueError(f"Custom prompts file does not exist: {prompts_path}")

    if not path.is_file():
        raise ValueError(f"Custom prompts path is not a file: {prompts_path}")

    if not path.suffix == ".py":
        raise ValueError(
            f"Custom prompts file must be a Python file (.py): {prompts_path}"
        )

    return path


def print_repository_status(auto_commit: AutoCommitAI) -> None:
    """Print detailed repository status."""
    repo_info = auto_commit.get_repository_info()

    if "error" in repo_info:
        print(f"❌ Error on repository status: {repo_info['error']}", file=sys.stderr)
        return

    status = repo_info["status"]
    print(f"\n{'='*60}")
    print(f"📊 REPOSITORY STATUS - Branch: {status['current_branch']}")
    print(f"📂 Path: {repo_info['repo_path']}")
    print(f"{'='*60}")

    # Files status
    if status["staged_files"]:
        print(f"📋 Staged files ({len(status['staged_files'])}):")
        for file in status["staged_files"]:
            print(f"   ✅ {file}")

    if status["unstaged_files"]:
        print(f"📝 Modified files ({len(status['unstaged_files'])}):")
        for file in status["unstaged_files"]:
            print(f"   📄 {file}")

    if status["untracked_files"]:
        print(f"❓ Untracked files ({len(status['untracked_files'])}):")
        for file in status["untracked_files"]:
            print(f"   🆕 {file}")

    if not any(
        [status["staged_files"], status["unstaged_files"], status["untracked_files"]]
    ):
        print("✨ Working directory clean - no changes detected")

    print(f"{'='*60}")


def print_commit_history(auto_commit: AutoCommitAI, count: int = 10) -> None:
    """Print recent commit history."""
    try:
        commits = auto_commit.git_utils.get_commit_history(max_count=count)

        print(f"\n{'='*60}")
        print(f"📚 RECENT COMMIT HISTORY ({len(commits)} commits)")
        print(f"{'='*60}")

        for commit in commits:
            print(f"🔹 {commit['hash']} - {commit['author']}")
            print(f"   📝 {commit['message']}")
            print(f"   🕐 {commit['date']}")
            print()

        print(f"{'='*60}")

    except Exception as e:
        print(f"❌ Error getting commit history: {e}", file=sys.stderr)

    except Exception as e:
        print(f"❌ Error getting branch information: {e}", file=sys.stderr)


def handle_preview_action(auto_commit: AutoCommitAI, args: argparse.Namespace) -> int:
    """Handle preview commit message action."""
    message = auto_commit.preview_commit_message(
        provider_name=args.provider,
        include_all=args.all,
        language=args.language,
        branch_name=args.branch_name,
        previous_commits=args.previous_commits,
        additional_context=args.additional_context,
    )

    return 0 if message else 1


def handle_stage_action(auto_commit: AutoCommitAI, args: argparse.Namespace) -> int:
    """Handle interactive staging action."""
    success = auto_commit.stage_interactive()

    return 0 if success else 1


def handle_commit_action(auto_commit: AutoCommitAI, args: argparse.Namespace) -> int:
    """Handle main commit generation action."""
    result = auto_commit.generate_and_commit(
        provider_name=args.provider,
        include_all=args.all,
        language=args.language,
        branch_name=args.branch_name,
        previous_commits=args.previous_commits,
        additional_context=args.additional_context,
        show_status=not args.no_status,
    )

    return 0 if result["success"] else 1


def create_auto_commit_instance(
    args: argparse.Namespace, config: Config, repo_path: str
) -> AutoCommitAI:
    """Create AutoCommitAI instance with optional custom prompts."""
    custom_prompts_path = None

    if args.custom_prompts:
        try:
            custom_prompts_path = validate_custom_prompts_path(args.custom_prompts)
            if args.verbose:
                print(f"🎯 Using custom prompts from: {custom_prompts_path}")
        except ValueError as e:
            raise ValueError(f"Custom prompts validation failed: {e}")

    return AutoCommitAI(config, repo_path, custom_prompts_path)


def main():
    """Main function to handle command line arguments and execute operations."""
    parser = setup_parser()
    args = parser.parse_args()

    try:
        # Validate repository path
        repo_path = validate_repository_path(args.repo)

        # Load configuration
        config = Config.from_env()

        # Create AutoCommitAI instance
        auto_commit = create_auto_commit_instance(args, config, str(repo_path))

        # Handle different actions
        if args.status:
            print_repository_status(auto_commit)
            return 0

        elif args.history:
            print_commit_history(auto_commit)
            return 0

        elif args.preview:
            return handle_preview_action(auto_commit, args)

        elif args.stage:
            return handle_stage_action(auto_commit, args)

        else:
            # Default action: generate and commit
            return handle_commit_action(auto_commit, args)

    except KeyboardInterrupt:
        print("\n\n🛑 Operation cancelled by user.", file=sys.stderr)
        return 130  # Standard exit code for SIGINT

    except ValueError as e:
        print(f"❌ Invalid argument: {e}", file=sys.stderr)
        return 2

    except Exception as e:
        if args.verbose if "args" in locals() else False:
            import traceback

            traceback.print_exc()
        else:
            print(f"❌ Error in main process: {e}", file=sys.stderr)
        return 1


def cli_entry_point():
    """Entry point for setuptools console scripts."""
    sys.exit(main())


if __name__ == "__main__":
    cli_entry_point()
