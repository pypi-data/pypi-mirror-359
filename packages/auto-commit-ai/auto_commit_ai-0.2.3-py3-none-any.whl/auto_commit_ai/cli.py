# ================================
# MAIN FUNCTION FOR CLI
# ================================

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from .core import AutoCommitAI, Config


def setup_parser() -> argparse.ArgumentParser:
    """Setup and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="🤖 Generate commit messages automatically using AI providers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🚀 Usage examples:
  %(prog)s                           # Generate commit for staged changes
  %(prog)s --all                     # Include all files (staged + unstaged + untracked)
  %(prog)s --provider google         # Use Google Gemini
  %(prog)s --language es             # Generate in Spanish
  %(prog)s --preview                 # Preview message without committing
  %(prog)s --status                  # Show repository status
  %(prog)s --stage                   # Interactive file staging
  %(prog)s --auto-confirm            # Skip confirmation prompts
  %(prog)s --repo /path/to/repo      # Work with specific repository
  %(prog)s --history                 # Show recent commit history
  %(prog)s --branches                # Show branch information
  %(prog)s --output json             # JSON output for automation

🔧 Providers: openai, google, azure
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

    action_group.add_argument(
        "--branches", action="store_true", help="Show branch information"
    )

    # Behavior modifiers
    parser.add_argument(
        "--auto-confirm",
        action="store_true",
        help="Skip user confirmation prompts (useful for automation)",
    )

    parser.add_argument(
        "--no-status",
        action="store_true",
        help="Don't show repository status before generating commit",
    )

    parser.add_argument(
        "--output",
        "-o",
        choices=["text", "json"],
        default="text",
        help="Output format (text for human-readable, json for automation)",
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


def print_json_output(data: dict) -> None:
    """Print data in JSON format."""
    print(json.dumps(data, indent=2, default=str))


def print_repository_status(auto_commit: AutoCommitAI) -> None:
    """Print detailed repository status."""
    repo_info = auto_commit.get_repository_info()

    if "error" in repo_info:
        print(f"❌ Error: {repo_info['error']}", file=sys.stderr)
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


def print_branch_info(auto_commit: AutoCommitAI) -> None:
    """Print branch information."""
    try:
        branches = auto_commit.git_utils.get_branches()

        print(f"\n{'='*60}")
        print(f"🌿 BRANCH INFORMATION")
        print(f"{'='*60}")

        print(f"🎯 Current branch: {branches['current']}")

        if branches["local"]:
            print(f"\n📍 Local branches ({len(branches['local'])}):")
            for branch in branches["local"]:
                marker = "👉 " if branch == branches["current"] else "   "
                print(f"{marker}{branch}")

        if branches["remote"]:
            print(f"\n🌐 Remote branches ({len(branches['remote'])}):")
            for branch in branches["remote"][:10]:  # Show max 10
                print(f"   {branch}")
            if len(branches["remote"]) > 10:
                print(f"   ... and {len(branches['remote']) - 10} more")

        print(f"{'='*60}")

    except Exception as e:
        print(f"❌ Error getting branch information: {e}", file=sys.stderr)


def handle_preview_action(auto_commit: AutoCommitAI, args: argparse.Namespace) -> int:
    """Handle preview commit message action."""
    message = auto_commit.preview_commit_message(
        provider_name=args.provider, include_all=args.all, language=args.language
    )

    if args.output == "json":
        print_json_output({"preview": message, "success": message is not None})

    return 0 if message else 1


def handle_stage_action(auto_commit: AutoCommitAI, args: argparse.Namespace) -> int:
    """Handle interactive staging action."""
    success = auto_commit.stage_interactive()

    if args.output == "json":
        print_json_output({"staged": success})

    return 0 if success else 1


def handle_commit_action(auto_commit: AutoCommitAI, args: argparse.Namespace) -> int:
    """Handle main commit generation action."""
    result = auto_commit.generate_and_commit(
        provider_name=args.provider,
        include_all=args.all,
        language=args.language,
        show_status=not args.no_status,
        auto_confirm=args.auto_confirm,
    )

    if args.output == "json":
        print_json_output(result)

    return 0 if result["success"] else 1


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
        auto_commit = AutoCommitAI(config, str(repo_path))

        # Handle different actions
        if args.status:
            if args.output == "json":
                print_json_output(auto_commit.get_repository_info())
            else:
                print_repository_status(auto_commit)
            return 0

        elif args.history:
            if args.output == "json":
                try:
                    commits = auto_commit.git_utils.get_commit_history(max_count=10)
                    print_json_output({"commits": commits})
                except Exception as e:
                    print_json_output({"error": str(e)})
                    return 1
            else:
                print_commit_history(auto_commit)
            return 0

        elif args.branches:
            if args.output == "json":
                try:
                    branches = auto_commit.git_utils.get_branches()
                    print_json_output({"branches": branches})
                except Exception as e:
                    print_json_output({"error": str(e)})
                    return 1
            else:
                print_branch_info(auto_commit)
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
            print(f"❌ Error: {e}", file=sys.stderr)
        return 1


def cli_entry_point():
    """Entry point for setuptools console scripts."""
    sys.exit(main())


if __name__ == "__main__":
    cli_entry_point()
