import unittest

from python.models import Commit
from python.stats import aggregate_authors


class AggregateAuthorsTests(unittest.TestCase):
    def test_empty_input(self):
        self.assertEqual(aggregate_authors([]), [])

    def test_counts_shares_sorting_and_timezone_order(self):
        commits = [
            Commit("1", "Alex", "2026-01-01T09:00:00+00:00", "Later"),
            Commit("2", "Zoe", "2026-01-02T00:00:00+00:00", "Zoe"),
            Commit("3", "Alex", "2026-01-01T10:00:00+02:00", "Earlier"),
            Commit("4", "Bob", "2026-01-03T00:00:00+00:00", "Bob"),
        ]
        
        stats = aggregate_authors(commits)

        self.assertEqual([item.author for item in stats], ["Alex", "Bob", "Zoe"])
        self.assertEqual([item.commit_count for item in stats], [2, 1, 1])
        self.assertEqual([item.share_percent for item in stats], [50.0, 25.0, 25.0])
        self.assertEqual(stats[0].first_commit, "2026-01-01T10:00:00+02:00")
        self.assertEqual(stats[0].last_commit, "2026-01-01T09:00:00+00:00")

    def test_invalid_or_naive_timestamps_are_rejected(self):
        for timestamp in ("", "not-a-date", "2026-01-01T10:00:00"):
            with self.subTest(timestamp=timestamp):
                commit = Commit("1", "Alex", timestamp, "Message")
                with self.assertRaises(ValueError):
                    aggregate_authors([commit])

    def test_single_author_has_full_share(self):
        commits = [
             Commit("1", "Alex", "2026-01-01T10:00:00+00:00", "First"),
           ]

        stats = aggregate_authors(commits)

        self.assertEqual(len(stats), 1)
        self.assertEqual(stats[0].commit_count, 1)
        self.assertEqual(stats[0].share_percent, 100.0)
        self.assertEqual(stats[0].first_commit, commits[0].date)
        self.assertEqual(stats[0].last_commit, commits[0].date)

    def test_sorting_prioritizes_count_then_case_sensitive_name(self):
        timestamp = "2026-01-01T10:00:00+00:00"
        commits = [
            Commit("1", "alex", timestamp, "One"),
            Commit("2", "Zoe", timestamp, "Two"),
            Commit("3", "Alex", timestamp, "Three"),
            Commit("4", "Zoe", timestamp, "Four"),
        ]

        stats = aggregate_authors(commits)

        self.assertEqual([item.author for item in stats], ["Zoe", "Alex", "alex"])
        self.assertEqual([item.commit_count for item in stats], [2, 1, 1])

    def test_fractional_share(self):
        timestamp = "2026-01-01T10:00:00+00:00"
        commits = [
            Commit("1", "Alex", timestamp, "One"),
            Commit("2", "Alex", timestamp, "Two"),
            Commit("3", "Bob", timestamp, "Three"),
        ]

        stats = aggregate_authors(commits)

        self.assertAlmostEqual(stats[0].share_percent, 200 / 3)
        self.assertAlmostEqual(stats[1].share_percent, 100 / 3)