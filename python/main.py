import argparse
import subprocess
import sys
from pathlib import Path

if __package__:
    from .git_parser import parse_git_log
    from .models import Repository
else:
    from git_parser import parse_git_log
    from models import Repository


def main() -> int:
    """Load commits from a local Git repository."""
    parser = argparse.ArgumentParser(description="Inspect a local Git repository.")
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        type=Path,
        help="Repository path (default: Current Directory)"
    )
    parser.add_argument(
        "--max-count",
        type=int,
        default=50,
        help="Maximum commits to load (default: 50)"
    )
    args = parser.parse_args()

    if args.max_count < 1:
        parser.error("--max-count must be a positive integer")

    try:
        repo = Repository(args.path)
    except OSError as exc:
        print(f"Repository path error: {exc!r}", file=sys.stderr)
        return 1

    try:
        parse_git_log(repo, args.max_count)
    except FileNotFoundError:
        print("Git could not be found; check that it is installed", file=sys.stderr)
        return 1
    except subprocess.TimeoutExpired:
        print("Git log timed out.", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as exc:
        print(
            f"Git log failed (exit {exc.returncode}): {exc.stderr!r}",
            file=sys.stderr
        )
        return 1
    except OSError as exc:
        print(f"Could not start Git: {exc!r}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Could not parse Git output: {exc!r}", file=sys.stderr)
        return 1

    print(f"Loaded commits: {repo.total_commits}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())