"""
DevPulse Core Data Models

This module defines the primary data structures representing Git entities:
- Commit: An immutable value object representing a single Git commit.
- Repository: An entity representing a Git repository and its associated commit history.
"""

from dataclasses import dataclass, field
from pathlib import Path

@dataclass(frozen=True)
class Commit:
    """Represents an immutable Git record.

    Attributes:
        hash (str): The Git commit hash (SHA-1 or SHA-256).
        author (str): The name/identity of the author.
        date (str): The commit timestamp as recorded by Git.
        message (str): The commit log message subject/body.

    Educational Note:
        Using `frozen=True` makes this dataclass immutable: fields cannot be reassigned
        after creation (e.g. `commit.hash = "..."` raises FrozenInstanceError).
        This mirrors Git's design where historical commits are cryptographically fixed.
    """

    hash: str
    author: str
    date: str
    message: str

    def __post_init__(self) -> None:
        """Validate commit fields upon initialization."""
        if not self.hash or not isinstance(self.hash, str):
            raise ValueError("Commit hash must be a non-empty string.")
        if not self.author or not isinstance(self.author, str):
            raise ValueError("Commit author must be a non-empty string.")

@dataclass
class Repository:
    """Represents a local Git repository and its collection of commits.

    Attributes:
        repo_path (Path): Path to the local repository directory.
        commits (list[Commit]): List of parsed commits associated with this repository.

    Educational Note:
        - `commits` uses `field(default_factory=list)` instead of `commits: list = []`.
          In Python, default arguments are evaluated once at definition time, so a bare
          mutable default like `[]` would accidentally be shared across all Repository instances!
        - `__post_init__` is a special dataclass lifecycle hook executed immediately after
          the generated `__init__` finishes. It is the recommended place for input validation
          and normalization.
    """
    repo_path: Path | str
    commits: list[Commit] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Resolve and Validate the repository filesystem path."""
        # Convert string to Path and resolve absolute path (prevents directory traversal ambiguities)
        resolved_path = Path(self.repo_path).resolve()

        # Security: Ensure the path actually exists and is a directory
        if not resolved_path.exists():
            raise FileNotFoundError(f"Repository path does not exist: {resolved_path}")
        if not resolved_path.is_dir():
            raise NotADirectoryError(f"Repository path is not a directory: {resolved_path}")

        # Store normalized Path instance
        self.repo_path = resolved_path

    def add_commit(self, commit: Commit) -> None:
        """Add a parsed Commit instance to the repository."""
        if not isinstance(commit, Commit):
            raise TypeError(f"Expected a Commit instance, got {type(commit).__name__}")
        self.commits.append(commit)

    @property
    def total_commits(self) -> int:
        """Return the total number of commits recorded."""
        return len(self.commits)

    