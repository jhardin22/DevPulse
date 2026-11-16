package main

import (
	"os"
	"path/filepath"
	"testing"
)

func TestRepositoryStoresCommitsIndependently(t *testing.T) {
	directory := t.TempDir()

	first, err := NewRepository(directory)
	if err != nil {
		t.Fatalf("creating first repository: %v", err)
	}
	second, err := NewRepository(directory)
	if err != nil {
		t.Fatalf("creating second repository: %v", err)
	}

	commit := Commit{
		Hash:    "abc123",
		Author:  "Alex",
		Date:    "2026-01-01",
		Message: "First commit",
	}
	first.AddCommit(commit)

	if got := first.TotalCommits(); got != 1 {
		t.Errorf("first repository has %d commits; want 1", got)
	}
	if got := second.TotalCommits(); got != 0 {
		t.Errorf("second repository has %d commits; want 0", got)
	}
}

func TestNewRepositoryRejectsInvalidPaths(t *testing.T) {
	directory := t.TempDir()
	filePath := filepath.Join(directory, "not-a-directory")

	if err := os.WriteFile(filePath, []byte("hello"), 0600); err != nil {
		t.Fatalf("creating test file: %v", err)
	}

	tests := []struct {
		name string
		path string
	}{
		{"missing path", filepath.Join(directory, "missing")},
		{"regular file", filePath},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			_, err := NewRepository(test.path)
			if err == nil {
				t.Error("expected an error, got nil")
			}
		})
	}
}
