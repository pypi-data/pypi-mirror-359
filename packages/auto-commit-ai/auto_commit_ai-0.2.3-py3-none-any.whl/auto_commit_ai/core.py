import sys
from pathlib import Path
from typing import Any, Dict, Optional

from .config import Config
from .git_utils import GitUtils
from .providers.factory import AIProviderFactory


class AutoCommitAI:
    """Automatic commit message generator using AI providers."""

    def __init__(self, config: Config, repo_path: str = "."):
        self.config = config
        self.git_utils = GitUtils(repo_path)
        self.repo_path = repo_path

    def _validate_repository(self) -> None:
        """Validate that we're in a Git repository."""
        if not self.git_utils.is_git_repo():
            raise Exception(f"Not in a Git repository: {self.repo_path}")

    def _get_ai_provider(self, provider_name: Optional[str] = None):
        """Get the AI provider instance."""
        provider_name = provider_name or self.config.default_provider
        try:
            return AIProviderFactory.create_provider(provider_name, self.config)
        except Exception as e:
            raise Exception(f"Error configuring AI provider '{provider_name}': {e}")

    def _check_changes(self, include_all: bool = False) -> tuple[bool, str]:
        """Check for changes and return diff content."""
        status = self.git_utils.get_status()

        if include_all:
            has_changes = (
                status["has_staged_changes"]
                or status["has_unstaged_changes"]
                or status["has_untracked_files"]
            )

            if not has_changes:
                return False, ""

            # Get comprehensive diff including untracked files
            diff_content = self.git_utils.get_all_diff()

            # Add untracked files content if any
            if status["untracked_files"]:
                diff_content += self._get_untracked_files_diff(
                    status["untracked_files"]
                )

        else:
            if not status["has_staged_changes"]:
                return False, ""
            diff_content = self.git_utils.get_staged_diff()

        return bool(diff_content.strip()), diff_content

    def _get_untracked_files_diff(self, untracked_files: list) -> str:
        """Generate diff-like content for untracked files."""
        diff_content = ""
        for file_path in untracked_files:
            try:
                full_path = Path(self.repo_path) / file_path
                if (
                    full_path.is_file() and full_path.stat().st_size < 1024 * 1024
                ):  # Skip files > 1MB
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    diff_content += f"\n+++ New file: {file_path}\n"
                    for i, line in enumerate(content.splitlines(), 1):
                        diff_content += f"+{i:4d}: {line}\n"
            except (OSError, UnicodeDecodeError):
                diff_content += f"\n+++ New binary/unreadable file: {file_path}\n"
        return diff_content

    def _display_repository_status(self) -> None:
        """Display current repository status."""
        status = self.git_utils.get_status()

        print(f"\n{'='*60}")
        print(f"REPOSITORY STATUS - Branch: {status['current_branch']}")
        print(f"{'='*60}")

        if status["staged_files"]:
            print(f"📋 Staged files ({len(status['staged_files'])}):")
            for file in status["staged_files"][:10]:  # Show max 10 files
                print(f"   • {file}")
            if len(status["staged_files"]) > 10:
                print(f"   ... and {len(status['staged_files']) - 10} more")

        if status["unstaged_files"]:
            print(f"📝 Modified files ({len(status['unstaged_files'])}):")
            for file in status["unstaged_files"][:10]:
                print(f"   • {file}")
            if len(status["unstaged_files"]) > 10:
                print(f"   ... and {len(status['unstaged_files']) - 10} more")

        if status["untracked_files"]:
            print(f"❓ Untracked files ({len(status['untracked_files'])}):")
            for file in status["untracked_files"][:10]:
                print(f"   • {file}")
            if len(status["untracked_files"]) > 10:
                print(f"   ... and {len(status['untracked_files']) - 10} more")

        print(f"{'='*60}")

    def _display_commit_message(self, commit_message: Dict[str, str]) -> None:
        """Display the generated commit message."""
        print(f"\n{'='*60}")
        print("🤖 GENERATED COMMIT MESSAGE")
        print(f"{'='*60}")
        print(f"📝 Title: {commit_message['title']}")
        if commit_message.get("description"):
            print(f"📄 Description:\n{commit_message['description']}")
        print(f"{'='*60}")

    def _get_user_confirmation(
        self, prompt: str, valid_yes: list = None, valid_no: list = None
    ) -> bool:
        """Get user confirmation with customizable responses."""
        if valid_yes is None:
            valid_yes = ["y", "yes", "sí", "si"]
        if valid_no is None:
            valid_no = ["n", "no"]

        while True:
            response = input(f"\n{prompt} (y/n): ").lower().strip()

            if response in valid_yes:
                return True
            elif response in valid_no:
                return False
            else:
                print("Please reply with 'y' to confirm or 'n' to cancel.")

    def _handle_post_commit_actions(self) -> None:
        """Handle actions after successful commit."""
        print("✅ Commit successful!")

        # Show recent commit history
        try:
            recent_commits = self.git_utils.get_commit_history(max_count=3)
            print("\n📚 Recent commits:")
            for commit in recent_commits:
                print(f"   {commit['hash']} - {commit['message'][:50]}...")
        except Exception:
            pass  # Don't fail if we can't get history

        # Ask about pushing
        if self._get_user_confirmation("🚀 Would you like to push the changes?"):
            try:
                self.git_utils.push_changes()
                print("📡 Changes pushed successfully!")
            except Exception as e:
                print(f"❌ Error pushing changes: {e}", file=sys.stderr)
                print("💡 You can push manually later with: git push")

    def get_repository_info(self) -> Dict[str, Any]:
        """Get comprehensive repository information."""
        try:
            self._validate_repository()
            status = self.git_utils.get_status()
            branches = self.git_utils.get_branches()
            recent_commits = self.git_utils.get_commit_history(max_count=5)

            return {
                "status": status,
                "branches": branches,
                "recent_commits": recent_commits,
                "repo_path": self.repo_path,
            }
        except Exception as e:
            return {"error": str(e)}

    def generate_and_commit(
        self,
        provider_name: Optional[str] = None,
        include_all: bool = False,
        language: Optional[str] = None,
        show_status: bool = True,
        auto_confirm: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate a commit message using an AI provider and commit changes.

        Args:
            provider_name: AI provider to use (defaults to config default)
            include_all: Include all changes (staged + unstaged + untracked)
            language: Language for the commit message
            show_status: Whether to show repository status
            auto_confirm: Skip user confirmation (useful for automation)

        Returns:
            Dict with operation results
        """
        result = {"success": False, "commit_hash": None, "message": None, "error": None}

        try:
            # Validate repository
            self._validate_repository()

            # Show repository status if requested
            if show_status:
                self._display_repository_status()

            # Get AI provider
            ai_provider = self._get_ai_provider(provider_name)

            # Check for changes
            has_changes, diff_content = self._check_changes(include_all)

            if not has_changes:
                message = (
                    "No changes to commit."
                    if include_all
                    else "No staged changes found. Please stage your changes or use --all flag."
                )
                print(f"ℹ️  {message}")
                result["message"] = message
                return result

            # Generate commit message
            print(
                f"🤖 Generating commit message with {ai_provider.__class__.__name__}..."
            )
            try:
                commit_message = ai_provider.generate_commit_message(
                    diff_content, language
                )
            except Exception as e:
                error_msg = f"Error generating commit message: {e}"
                print(f"❌ {error_msg}", file=sys.stderr)
                result["error"] = error_msg
                return result

            # Display generated message
            self._display_commit_message(commit_message)

            # Get user confirmation (unless auto-confirm is enabled)
            if not auto_confirm:
                if not self._get_user_confirmation("✨ Use this commit message?"):
                    print("🚫 Commit cancelled.")
                    result["message"] = "Commit cancelled by user"
                    return result

            # Stage all changes if requested
            if include_all:
                print("📋 Staging all changes...")
                self.git_utils.stage_all_changes()

            # Create commit
            try:
                commit_hash = self.git_utils.commit_with_message(commit_message)
                result["success"] = True
                result["commit_hash"] = commit_hash
                result["message"] = commit_message

                # Handle post-commit actions
                if not auto_confirm:
                    self._handle_post_commit_actions()
                else:
                    print(f"✅ Commit successful! Hash: {commit_hash[:8]}")

            except Exception as e:
                error_msg = f"Error creating commit: {e}"
                print(f"❌ {error_msg}", file=sys.stderr)
                result["error"] = error_msg

        except Exception as e:
            error_msg = str(e)
            print(f"❌ {error_msg}", file=sys.stderr)
            result["error"] = error_msg

        return result

    def preview_commit_message(
        self,
        provider_name: Optional[str] = None,
        include_all: bool = False,
        language: Optional[str] = None,
    ) -> Optional[Dict[str, str]]:
        """
        Generate and preview a commit message without committing.

        Returns:
            Generated commit message or None if error
        """
        try:
            self._validate_repository()

            # Get AI provider
            ai_provider = self._get_ai_provider(provider_name)

            # Check for changes
            has_changes, diff_content = self._check_changes(include_all)

            if not has_changes:
                print("ℹ️  No changes found to generate commit message for.")
                return None

            # Generate commit message
            print(
                f"🤖 Generating commit message preview with {ai_provider.__class__.__name__}..."
            )
            commit_message = ai_provider.generate_commit_message(diff_content, language)

            # Display message
            self._display_commit_message(commit_message)

            return commit_message

        except Exception as e:
            print(f"❌ Error generating commit message preview: {e}", file=sys.stderr)
            return None

    def stage_interactive(self) -> bool:
        """Interactive staging of files."""
        try:
            status = self.git_utils.get_status()

            if not (status["unstaged_files"] or status["untracked_files"]):
                print("ℹ️  No unstaged files to stage.")
                return False

            print("\n📝 Files available for staging:")
            all_files = status["unstaged_files"] + status["untracked_files"]

            for i, file in enumerate(all_files, 1):
                file_status = (
                    "modified" if file in status["unstaged_files"] else "untracked"
                )
                print(f"  {i:2d}. {file} ({file_status})")

            while True:
                selection = input(
                    "\nEnter file numbers to stage (e.g., 1,3-5,7) or 'all' for all files: "
                ).strip()

                if selection.lower() == "all":
                    self.git_utils.stage_files(all_files)
                    print(f"✅ Staged all {len(all_files)} files.")
                    return True

                try:
                    # Parse selection (e.g., "1,3-5,7")
                    files_to_stage = []
                    for part in selection.split(","):
                        part = part.strip()
                        if "-" in part:
                            start, end = map(int, part.split("-"))
                            files_to_stage.extend(
                                all_files[i - 1] for i in range(start, end + 1)
                            )
                        else:
                            files_to_stage.append(all_files[int(part) - 1])

                    self.git_utils.stage_files(files_to_stage)
                    print(f"✅ Staged {len(files_to_stage)} files.")
                    return True

                except (ValueError, IndexError):
                    print("❌ Invalid selection. Please try again.")

        except Exception as e:
            print(f"❌ Error during interactive staging: {e}", file=sys.stderr)
            return False
