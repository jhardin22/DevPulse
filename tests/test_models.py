import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path
from tempfile import TemporaryDirectory

from python.models import Commit, Repository


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