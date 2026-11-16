package main

import "testing"

func TestNewCommit(t *testing.T) {
	commit, err := NewCommit("abc123", "Alex", "2026-01-01", "First commit")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if commit.Hash != "abc123" || commit.Author != "Alex" ||
		commit.Date != "2026-01-01" || commit.Message != "First commit" {
		t.Errorf("commit fields were not preserved: %+v", commit)
	}
}

func TestNewCommitRejectsEmptyIdentity(t *testing.T) {
	tests := []struct {
		name   string
		hash   string
		author string
	}{
		{"empty hash", "", "Alex"},
		{"empty author", "abc123", ""},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			_, err := NewCommit(test.hash, test.author, "2026-01-01", "Message")
			if err == nil {
				t.Error("expected and error, got nil")
			}
		})
	}
}
