import unittest
from unittest.mock import patch
import subprocess
from tempfile import TemporaryDirectory

from python.git_parser import parse_records, parse_git_log
from python.models import Commit, Repository


class ParseRecordsTests(unittest.TestCase):
    def test_empty_output_returns_no_commits(self):
        self.assertEqual(parse_records(""), [])

    def test_parses_multiple_commits_and_preserves_message_body(self):
        fields = [
            "abc123", "Alex", "2026-01-01", "Subject\n\nBody\n",
            "def456", "Sam", "2026-01-02", "Another commit\n"
        ]
        raw_output = "\0".join(fields) + "\0"

        self.assertEqual(
            parse_records(raw_output),
            [
               Commit("abc123", "Alex", "2026-01-01", "Subject\n\nBody\n"),
               Commit("def456", "Sam", "2026-01-02", "Another commit\n"), 
            ],
        )

    def test_rejects_missing_final_terminator(self):
        with self.assertRaises(ValueError):
            parse_records("\0".join(["abc123", "Alex", "2026-01-01", "Message"]))

class GitIntegrationTests(unittest.TestCase):
    def test_reads_full_message_without_adding_duplicates(self):
        with TemporaryDirectory() as directory:
            subprocess.run(["git", "init", "-q", directory], check=True)
            subprocess.run(
                [
                    "git", "-C", directory,
                    "-c", "user.name=Test Author",
                    "-c", "user.email=test@example.invalid",
                    "-c", "commit.gpgsign=false",
                    "commit", "--allow-empty", "-q",
                    "-m", "Subject", "-m", "Body",
                ],
                check=True,
            )

            repo = Repository(directory)
            first = parse_git_log(repo)
            second = parse_git_log(repo)

            self.assertEqual(len(first), 1)
            self.assertEqual(first[0].author, "Test Author")
            self.assertEqual(first[0].message, "Subject\n\nBody\n")
            self.assertEqual(first, second)
            self.assertEqual(repo.total_commits, 1)

class GitValidationTests(unittest.TestCase):
    def test_invalid_max_count_does_not_run_git(self):
        with TemporaryDirectory() as directory:
            repo = Repository(directory)

            with patch("python.git_parser.run_git_log") as run_git_log:
                for invalid_count in (0, -1, True):
                    with self.subTest(max_count=invalid_count):
                        with self.assertRaises(ValueError):
                            parse_git_log(repo, invalid_count)
                
                run_git_log.assert_not_called