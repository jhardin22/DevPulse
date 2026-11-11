import functools
import subprocess
import time
from pathlib import Path
from typing import Any, Callable

if __package__:
    from .models import Commit, Repository
else:
    from models import Commit, Repository


def time_execution(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator that measures and prints the execution duration of a function.

    Args:
        func: The function being wrapped.

    Returns:
        The wrapped function with timing behavior attached.

    Educational Note:
        - `@functools.wraps(func)` preserves the wrapped function's identity
          (__name__, __doc__, and type annotations).
        - `*args` and `**kwargs` ensure this wrapper can accept any parameters
          that `func` expects.
        - `time.perf_counter()` provides high-resolution, monotonic timing.
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()

        result = func(*args, **kwargs)

        elapsed_time = time.perf_counter() - start_time
        print(f"[TIMING] '{func.__name__}' took {elapsed_time:.4f}s to execute")

        return result

    return wrapper

FIELD_SEP = "%x00"
GIT_LOG_FORMAT = f"%H{FIELD_SEP}%an{FIELD_SEP}%aI{FIELD_SEP}%B"

def run_git_log(repo_path: Path, max_count: int) -> str:
    """Run gitlog safely and return its raw stdout."""
    cmd = [
        "git", 
        "-C", str(repo_path),
        "log",
        "-z",
        f"--max-count={max_count}", 
        f"--pretty=tformat:{GIT_LOG_FORMAT}",
    ]
    result = subprocess.run(
        cmd, capture_output=True, text=True, check=True, timeout=30,
    )
    return result.stdout

def parse_records(raw_output: str) -> list[Commit]:
    """Convert NUL-separated Git fields into Commit objects."""
    if not raw_output:
        return []

    if not raw_output.endswith("\0"):
        raise ValueError("Git output is missing its final NUL terminator.")

    fields = raw_output[:-1].split("\0")

    if len(fields) % 4 != 0:
        raise ValueError("Git output must contain four fields per commit.")
    
    commits: list[Commit] = []
    for index in range(0,len(fields), 4):
        hash_, author, date, message = fields[index:index + 4]
        commits.append(Commit(hash=hash_, author=author, date=date, message=message))
    return commits


@time_execution
def parse_git_log(repo: Repository, max_count: int = 50) -> list[Commit]:
    """Populate `repo` with up to `max_count` commits and return them."""
    if isinstance(max_count, bool) or not isinstance(max_count, int) or max_count < 1:
        raise ValueError("max_count must be a positive integer.")
    commits = parse_records(run_git_log(repo.repo_path, max_count))

    existing_hashes = {commit.hash for commit in repo.commits}

    for commit in commits:
        if commit.hash not in existing_hashes:
            repo.add_commit(commit)
            existing_hashes.add(commit.hash)
    return commits