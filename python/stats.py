from datetime import datetime

if __package__:
    from .models import AuthorStats, Commit
else:
    from models import AuthorStats, Commit


def aggregate_authors(commits: list[Commit]) -> list[AuthorStats]:
    """Summmarize commites by author, ordered by count and then name."""
    timestamps_by_author: dict[str, list[tuple[datetime, str]]] = {}

    for commit in commits:
        if not isinstance(commit.date, str):
            raise ValueError("Commit timestamp must be a string.")

        try:
            timestamp = datetime.fromisoformat(commit.date)
        except ValueError as exc:
            raise ValueError(f"invalid commit timestamp: {commit.date!r}") from exc

        if timestamp.utcoffset() is None:
            raise ValueError(f"commit timestamp must include a timezone: {commit.date!r}")

        timestamps_by_author.setdefault(commit.author, []).append(
            (timestamp, commit.date)
        )

    results: list[AuthorStats] = []

    for author, timestamps in timestamps_by_author.items():
        first = min(timestamps, key=lambda item: item[0])
        last = max(timestamps, key=lambda item: item[0])
        count = len(timestamps)

        results.append(
            AuthorStats(
                author=author,
                commit_count=count,
                share_percent=count * 100.0 / len(commits),
                first_commit=first[1],
                last_commit=last[1],
            )
        )
    return sorted(results, key=lambda stats: (-stats.commit_count, stats.author))