import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path
from tempfile import TemporaryDirectory

from python.models import Commit, Repository, AuthorStats


class CommitTests(unittest.TestCase):
    def test_commit_is_immutable(self):
        commit = Commit("abc123", "Alex", "2026-01-01", "First commit")

        with self.assertRaises(FrozenInstanceError):
            commit.author = "Someone else"

    def test_empty_author_is_rejected(self):
        with self.assertRaises(ValueError):
            Commit("abc123", "", "2026-01-01", "First commit")

    def test_invalid_hash_and_author_are_rejected(self):
        cases = [
            ("", "Alex"),
            (123, "Alex"),
            ("abc123", 123),
        ]

        for hash_value, author in cases:
            with self.subTest(hash_value=hash_value, author=author):
                with self.assertRaises(ValueError):
                    Commit(hash_value, author, "2026-01-01", "Message")


class RepositoryTests(unittest.TestCase):
    def test_repositories_have_independent_commit_lists(self):
        with TemporaryDirectory() as directory:
            first = Repository(directory)
            second = Repository(directory)
            first.add_commit(Commit("abc123", "Alex", "2026-01-01", "First commit"))

            self.assertEqual(first.total_commits, 1)
            self.assertEqual(second.total_commits, 0)

    def test_path_is_normalized(self):
        with TemporaryDirectory() as directory:
            repo = Repository(directory)
            self.assertEqual(repo.repo_path, Path(directory).resolve())

    def test_missing_path_and_file_are_rejected(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            file_path = root / "example.txt"
            file_path.write_text("hello")

            with self.assertRaises(FileNotFoundError):
                Repository(root / "missing")

            with self.assertRaises(NotADirectoryError):
                Repository(file_path)

    def test_rejects_non_commit_objects(self):
        with TemporaryDirectory() as directory:
            repo = Repository(directory)

            with self.assertRaises(TypeError):
                repo.add_commit("not a commit")

            self.assertEqual(repo.total_commits, 0)

class AuthorStatsTests(unittest.TestCase):
    def setUp(self):
        self.valid_fields = {
            "author": "Alex",
            "commit_count": 2,
            "share_percent": 50.0,
            "first_commit": "2026-01-01T10:00:00+00:00",
            "last_commit": "2026-01-02T10:00:00+00:00",
        }

    def test_valid_stats_and_equality(self):
        stats = AuthorStats(**self.valid_fields)

        self.assertEqual(stats.author, "Alex")
        self.assertEqual(stats.commit_count, 2)
        self.assertEqual(stats.share_percent, 50.0)
        self.assertEqual(stats.first_commit, self.valid_fields["first_commit"])
        self.assertEqual(stats.last_commit, self.valid_fields["last_commit"])
        self.assertEqual(stats, AuthorStats(**self.valid_fields))

    def test_stats_are_immutable(self):
        stats = AuthorStats(**self.valid_fields)

        with self.assertRaises(FrozenInstanceError):
            stats.author = "Someone Else"

    def test_valid_share_boundaries(self):
        for share in (0, 0.0, 100, 100.0):
            with self.subTest(share=share):
                fields = {**self.valid_fields, "share_percent": share}
                self.assertEqual(AuthorStats(**fields).share_percent, share)

    def test_invalid_fields_are_rejected(self):
        cases = {
            "author": ("", 123, None),
            "commit_count": (0, -1, True, 1.5, "2", None),
            "share_percent": (-0.1, 100.1, True, "50", None,
                              float("nan"), float("inf"), float("-inf")),
            "first_commit": ("", 123, None),
            "last_commit": ("", 123, None),
        }

        for field, invalid_values in cases.items():
            for value in invalid_values:
                with self.subTest(field=field, value=value):
                    fields = {**self.valid_fields, field: value}
                    with self.assertRaises(ValueError):
                        AuthorStats(**fields)