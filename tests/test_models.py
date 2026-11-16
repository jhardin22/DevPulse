import unittest
from dataclasses import FrozenInstanceError
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


class RepositoryTests(unittest.TestCase):
    def test_repositories_have_independent_commit_lists(self):
        with TemporaryDirectory() as directory:
            first = Repository(directory)
            second = Repository(directory)
            first.add_commit(Commit("abc123", "Alex", "2026-01-01", "First commit"))

            self.assertEqual(first.total_commits, 1)
            self.assertEqual(second.total_commits, 0)