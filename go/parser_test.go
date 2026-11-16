package main

import "testing"

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