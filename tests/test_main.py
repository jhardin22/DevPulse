import io
import subprocess
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from python.main import main

class MainCLITests(unittest.TestCase):
    def test_loads_loads_commit_from_valid_repository(self):
        with TemporaryDirectory() as directory:
            subprocess.run(["git", "init", "-q", directory], check=True)
            subprocess.run(
                [
                    "git", "-C", directory,
                    "-c", "user.name=Test Author",
                    "-c", "user.email=test@example.invalid",
                    "-c", "commit.gpgsign=false",
                    "commit", "--allow-empty", "-q", "-m", "Initial commit",
                ],
                check=True,
            )

            stdout = io.StringIO()
            with patch.object(sys, "argv", ["devpulse", directory, "--max-count", "5"]):
                with redirect_stdout(stdout):
                    exit_code = main()

            self.assertEqual(exit_code, 0)
            self.assertIn("Loaded commits: 1", stdout.getvalue())

    def test_missing_path_returns_error_exit_code(self):
        with TemporaryDirectory() as directory:
             missing_path = str(Path(directory) / "does-not-exist")
             stderr = io.StringIO()

             with patch.object(sys, "argv", ["devpulse", missing_path]):
                 with redirect_stderr(stderr):
                     exit_code = main()

             self.assertEqual(exit_code, 1)
             self.assertIn("Repository path error:", stderr.getvalue())

    def test_non_git_directory_returns_error_exit_code(self):
        with TemporaryDirectory() as directory:
            stderr = io.StringIO()

            with patch.object(sys, "argv", ["devpulse", directory]):
                with redirect_stderr(stderr):
                    exit_code = main()

            self.assertEqual(exit_code, 1)
            self.assertIn("Git log failed", stderr.getvalue())

    def test_invalid_max_count_exits_with_code_2(self):
        stderr = io.StringIO()

        with patch.object(sys, "argv", ["devpulse", ".", "--max-count", "0"]):
            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as context:
                    main()

        self.assertEqual(context.exception.code, 2)

    def test_reports_git_startup_and_timeout_errors(self):
        cases = [
            (FileNotFoundError(), "Git could not be found"),
            (subprocess.TimeoutExpired("git", 30), "Git log timed out"),
        ]

        with TemporaryDirectory() as directory:
            for error, expected_message in cases:
                with self.subTest(error=type(error).__name__):
                    stderr = io.StringIO()

                    with patch.object(sys, "argv", ["devpulse", directory]):
                        with patch("python.main.parse_git_log", side_effect=error):
                            with redirect_stderr(stderr):
                                exit_code = main()

                    self.assertEqual(exit_code, 1)
                    self.assertIn(expected_message, stderr.getvalue())

    def test_both_cli_launch_styles(self):
        project_root = Path(__file__).resolve().parents[1]

        with TemporaryDirectory() as directory:
            subprocess.run(["git", "init", "-q", directory], check=True)
            subprocess.run(
                [
                    "git", "-C", directory,
                    "-c", "user.name=Test Author",
                    "-c", "user.email=test@example.invalid",
                    "-c", "commit.gpgsign=false",
                    "commit", "--allow-empty", "-q", "-m", "Initial commit",
                ],
                check=True,
            )

            for arguments in (["-m", "python.main"], ["python/main.py"]):
                with self.subTest(arguments=arguments):
                    result = subprocess.run(
                        [sys.executable, *arguments, directory],
                        cwd=project_root,
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )

                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn("Loaded commits: 1", result.stdout)