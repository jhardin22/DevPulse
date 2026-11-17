package main

import (
	"os/exec"
	"testing"
)

func TestParseRecordsEmptyOutput(t *testing.T) {
	commits, err := ParseRecords("")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if len(commits) != 0 {
		t.Errorf("got %d commits; want 0", len(commits))
	}
}

func TestParseRecordsPreservesMessageBody(t *testing.T) {
	raw := "abc123\x00Alex\x002026-01-01\x00Subject\n\nBody\n\x00"

	commits, err := ParseRecords(raw)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(commits) != 1 {
		t.Fatalf("got %2d commits; want 1", len(commits))
	}

	commit := commits[0]
	if commit.Hash != "abc123" || commit.Author != "Alex" ||
		commit.Date != "2026-01-01" || commit.Message != "Subject\n\nBody\n" {
		t.Errorf("unexpected commit: %+v", commit)
	}
}

func TestParseRecordsRejectsMalformedOutput(t *testing.T) {
	tests := []struct {
		name string
		raw  string
	}{
		{"missing final terminator", "abc123\x00Alex\x002026-01-01\x00Message"},
		{"missing field", "abc123\x00Alex\x002026-01-01\x00"},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			_, err := ParseRecords(test.raw)
			if err == nil {
				t.Error("expected an error, got nil")
			}
		})
	}
}

func TestParseRecordsMultipleCommits(t *testing.T) {
	raw := "abc123\x00Alex\x002026-01-01\x00First\n\x00" +
		"def456\x00Sam\x002026-01-02\x00Second\n\x00"

	commits, err := ParseRecords(raw)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(commits) != 2 {
		t.Fatalf("got %d commits; want 2", len(commits))
	}

	if commits[0].Hash != "abc123" || commits[1].Hash != "def456" {
		t.Errorf("commits missing or out of order: %+v", commits)
	}
}

func runTestGit(t *testing.T, args ...string) {
	t.Helper()
	cmd := exec.Command("git", args...)
	output, err := cmd.CombinedOutput()
	if err != nil {
		t.Fatalf("git failed: %v\n%s", err, output)
	}
}

func TestParseGitLogLoadsWithoutDuplicates(t *testing.T) {
	directory := t.TempDir()

	runTestGit(t, "init", "-q", directory)

	for _, msg := range []string{"First", "Second"} {
		runTestGit(
			t,
			"-C", directory,
			"-c", "user.name=Test Author",
			"-c", "user.email=test@example.invalid",
			"-c", "commit.gpgsign=false",
			"commit", "--allow-empty", "-q", "-m", msg,
		)
	}

	repo, err := NewRepository(directory)
	if err != nil {
		t.Fatalf("creating repository: %v", err)
	}

	latest, err := ParseGitLog(repo, 1)
	if err != nil {
		t.Fatalf("loading latest commit: %v", err)
	}
	if len(latest) != 1 {
		t.Fatalf("got %d commits; want 1", len(latest))
	}
	if latest[0].Message != "Second\n" {
		t.Errorf("got message %q; want %q", latest[0].Message, "Second\n")
	}
	if got := repo.TotalCommits(); got != 1 {
		t.Errorf("repository has %d commits; want 1", got)
	}

	all, err := ParseGitLog(repo, 2)
	if err != nil {
		t.Fatalf("loading both commits: %v", err)
	}
	if len(all) != 2 {
		t.Errorf("got %d commits; want 2", len(all))
	}
	if got := repo.TotalCommits(); got != 2 {
		t.Errorf("repository has %d commits; want 2", got)
	}
}

func TestParseGitLogRejectsInvalidCount(t *testing.T) {
	directory := t.TempDir()
	runTestGit(t, "init", "-q", directory)
	runTestGit(
		t,
		"-C", directory,
		"-c", "user.name=Test Author",
		"-c", "user.email=test@example.invalid",
		"-c", "commit.gpgsign=false",
		"commit", "--allow-empty", "-q", "-m", "Initial commit",
	)

	repo, err := NewRepository(directory)
	if err != nil {
		t.Fatalf("creating repository: %v", err)
	}

	for _, count := range []int{0, -1} {
		_, err := ParseGitLog(repo, count)
		if err == nil {
			t.Errorf("count %d: expected an error", count)
		}
	}

	if got := repo.TotalCommits(); got != 0 {
		t.Errorf("repository has %d commits; want 0", got)
	}
}

func TestParseGitLogRejectsNonGitDirectory(t *testing.T) {
	repo, err := NewRepository(t.TempDir())
	if err != nil {
		t.Fatalf("creating repository: %v", err)
	}

	_, err = ParseGitLog(repo, 10)
	if err == nil {
		t.Error("expected an error for non-git directory, got nil")
	}

	if got := repo.TotalCommits(); got != 0 {
		t.Errorf("repository has %d commits; want 0", got)
	}
}

func TestParseGitLogPreservesFullMessage(t *testing.T) {
	directory := t.TempDir()
	runTestGit(t, "init", "-q", directory)
	runTestGit(
		t,
		"-C", directory,
		"-c", "user.name=Test Author",
		"-c", "user.email=test@example.invalid",
		"-c", "commit.gpgsign=false",
		"commit", "--allow-empty", "-q",
		"-m", "Subject", "-m", "Body",
	)

	repo, err := NewRepository(directory)
	if err != nil {
		t.Fatalf("creating repository: %v", err)
	}

	commits, err := ParseGitLog(repo, 1)
	if err != nil {
		t.Fatalf("loading commit: %v", err)
	}
	if len(commits) != 1 {
		t.Fatalf("got %d commits; want 1", len(commits))
	}

	if commits[0].Author != "Test Author" {
		t.Errorf("got author %q; want %q", commits[0].Author, "Test Author")
	}
	if commits[0].Message != "Subject\n\nBody\n" {
		t.Errorf("got message %q; want %q", commits[0].Message, "Subject\n\nBody\n")
	}
}
