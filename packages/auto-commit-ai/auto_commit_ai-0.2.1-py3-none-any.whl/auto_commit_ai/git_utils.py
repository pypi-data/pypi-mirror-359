import json
import os
from typing import Any, Dict

from git import GitCommandError, InvalidGitRepositoryError, Repo
from git.exc import GitError


class GitUtils:
    """Utilities for interacting with Git repositories using GitPython."""

    def __init__(self, repo_path: str = "."):
        """Initialize GitUtils with a repository path."""
        self.repo_path = repo_path
        self._repo = None

    @property
    def repo(self) -> Repo:
        """Get or create the Git repository object."""
        if self._repo is None:
            try:
                self._repo = Repo(self.repo_path)
            except InvalidGitRepositoryError:
                raise Exception(f"Not a Git repository: {self.repo_path}")
        return self._repo

    @staticmethod
    def is_git_repo(path: str = ".") -> bool:
        """Checks if the given directory is a Git repository."""
        try:
            Repo(path)
            return True
        except InvalidGitRepositoryError:
            return False

    def get_staged_diff(self) -> str:
        """Gets the diff of staged files."""
        try:
            # Get staged changes (index vs HEAD)
            diff = self.repo.git.diff("--cached")
            return diff
        except GitCommandError as e:
            raise Exception(f"Error getting staged diff: {e}")

    def get_all_diff(self) -> str:
        """Gets the diff of all changes (staged and unstaged)."""
        try:
            # Get all changes compared to HEAD
            diff = self.repo.git.diff("HEAD")
            return diff
        except GitCommandError as e:
            raise Exception(f"Error getting all diff: {e}")

    def get_unstaged_diff(self) -> str:
        """Gets the diff of unstaged files only."""
        try:
            # Get unstaged changes (working tree vs index)
            diff = self.repo.git.diff()
            return diff
        except GitCommandError as e:
            raise Exception(f"Error getting unstaged diff: {e}")

    def has_staged_changes(self) -> bool:
        """Checks if there are staged changes."""
        try:
            # Check if index differs from HEAD
            return len(list(self.repo.index.diff("HEAD"))) > 0
        except Exception:
            return False

    def has_unstaged_changes(self) -> bool:
        """Checks if there are unstaged changes."""
        try:
            # Check if working tree differs from index
            return len(list(self.repo.index.diff(None))) > 0
        except Exception:
            return False

    def has_untracked_files(self) -> bool:
        """Checks if there are untracked files."""
        try:
            return len(self.repo.untracked_files) > 0
        except Exception:
            return False

    def get_status(self) -> Dict[str, Any]:
        """Gets comprehensive repository status."""
        try:
            return {
                "staged_files": [item.a_path for item in self.repo.index.diff("HEAD")],
                "unstaged_files": [item.a_path for item in self.repo.index.diff(None)],
                "untracked_files": self.repo.untracked_files,
                "current_branch": self.repo.active_branch.name,
                "is_dirty": self.repo.is_dirty(),
                "has_staged_changes": self.has_staged_changes(),
                "has_unstaged_changes": self.has_unstaged_changes(),
                "has_untracked_files": self.has_untracked_files(),
            }
        except Exception as e:
            raise Exception(f"Error getting repository status: {e}")

    def stage_all_changes(self):
        """Adds all changes to the staging area."""
        try:
            # Stage all tracked files (modified and deleted)
            self.repo.git.add("-u")
            # Stage all untracked files
            self.repo.git.add("-A")
        except GitCommandError as e:
            raise Exception(f"Error staging changes: {e}")

    def stage_files(self, files: list):
        """Stages specific files."""
        try:
            self.repo.index.add(files)
        except GitCommandError as e:
            raise Exception(f"Error staging files {files}: {e}")

    def unstage_files(self, files: list):
        """Unstages specific files."""
        try:
            self.repo.git.reset("HEAD", *files)
        except GitCommandError as e:
            raise Exception(f"Error unstaging files {files}: {e}")

    def commit_with_message(self, message: Dict[str, str]):
        """Commits changes with the given message."""
        try:
            if not self.has_staged_changes():
                raise Exception("No staged changes to commit")

            # Create commit message
            if isinstance(message, dict):
                commit_msg = message.get("title", "")
                if "description" in message and message["description"]:
                    commit_msg += f"\n\n{message['description']}"
            else:
                commit_msg = str(message)

            # Commit the changes
            commit = self.repo.index.commit(commit_msg)
            return commit.hexsha
        except GitCommandError as e:
            raise Exception(f"Error committing changes: {e}")

    def push_changes(self, remote: str = "origin", branch: str = None):
        """Pushes the committed changes to the remote repository."""
        try:
            print("Attempting to push changes...")

            # Get current branch if not specified
            if branch is None:
                branch = self.repo.active_branch.name

            # Get remote object
            remote_obj = self.repo.remote(remote)

            # Push changes
            push_info = remote_obj.push(branch)

            # Check push results
            for info in push_info:
                if info.flags & info.ERROR:
                    raise Exception(f"Push failed: {info.summary}")
                elif info.flags & info.REJECTED:
                    raise Exception(f"Push rejected: {info.summary}")

            print("✅ Push successful!")
            return True

        except GitCommandError as e:
            raise Exception(
                f"Error pushing changes: {e}\nPlease check your remote configuration and permissions."
            )
        except Exception as e:
            raise Exception(f"An unexpected error occurred during push: {e}")

    def pull_changes(self, remote: str = "origin", branch: str = None):
        """Pulls changes from the remote repository."""
        try:
            print("Attempting to pull changes...")

            # Get current branch if not specified
            if branch is None:
                branch = self.repo.active_branch.name

            # Get remote object
            remote_obj = self.repo.remote(remote)

            # Pull changes
            pull_info = remote_obj.pull(branch)

            print("✅ Pull successful!")
            return pull_info

        except GitCommandError as e:
            raise Exception(f"Error pulling changes: {e}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred during pull: {e}")

    def get_commit_history(self, max_count: int = 10):
        """Gets recent commit history."""
        try:
            commits = []
            for commit in self.repo.iter_commits(max_count=max_count):
                commits.append(
                    {
                        "hash": commit.hexsha[:8],
                        "message": commit.message.strip(),
                        "author": str(commit.author),
                        "date": commit.authored_datetime.isoformat(),
                    }
                )
            return commits
        except Exception as e:
            raise Exception(f"Error getting commit history: {e}")

    def get_branches(self):
        """Gets all branches (local and remote)."""
        try:
            local_branches = [branch.name for branch in self.repo.branches]
            remote_branches = [ref.name for ref in self.repo.remote().refs]

            return {
                "local": local_branches,
                "remote": remote_branches,
                "current": self.repo.active_branch.name,
            }
        except Exception as e:
            raise Exception(f"Error getting branches: {e}")

    def create_branch(self, branch_name: str, checkout: bool = True):
        """Creates a new branch."""
        try:
            new_branch = self.repo.create_head(branch_name)
            if checkout:
                new_branch.checkout()
            return new_branch.name
        except Exception as e:
            raise Exception(f"Error creating branch {branch_name}: {e}")

    def checkout_branch(self, branch_name: str):
        """Switches to a different branch."""
        try:
            self.repo.git.checkout(branch_name)
            return self.repo.active_branch.name
        except GitCommandError as e:
            raise Exception(f"Error checking out branch {branch_name}: {e}")


# Funciones de conveniencia para uso estático (compatibilidad con la versión original)
def is_git_repo(path: str = ".") -> bool:
    """Static method to check if directory is a Git repository."""
    return GitUtils.is_git_repo(path)


def get_staged_diff(path: str = ".") -> str:
    """Static method to get staged diff."""
    git_utils = GitUtils(path)
    return git_utils.get_staged_diff()


def get_all_diff(path: str = ".") -> str:
    """Static method to get all diff."""
    git_utils = GitUtils(path)
    return git_utils.get_all_diff()


def has_staged_changes(path: str = ".") -> bool:
    """Static method to check for staged changes."""
    git_utils = GitUtils(path)
    return git_utils.has_staged_changes()


def stage_all_changes(path: str = "."):
    """Static method to stage all changes."""
    git_utils = GitUtils(path)
    git_utils.stage_all_changes()


def commit_with_message(message: Dict[str, str], path: str = "."):
    """Static method to commit with message."""
    git_utils = GitUtils(path)
    return git_utils.commit_with_message(message)


def push_changes(path: str = ".", remote: str = "origin", branch: str = None):
    """Static method to push changes."""
    git_utils = GitUtils(path)
    return git_utils.push_changes(remote, branch)
