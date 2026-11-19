package main

import (
	"bytes"
	"path/filepath"
	"strings"
	"testing"
)

func TestRunLoadsCommits(t *testing.T) {
	directory := t.TempDir()
	runTestGit(t, "init", "-q", directory)

	for _, message := range []string{"First", "Second"} {
		runTestGit(
			t,
			"-C", directory,
			"-c", "user.name=Test Author",
			"-c", "user.email=test@example.invalid",
			"-c", "commit.gpgsign=false",
			"commit", "--allow-empty", "-q", "-m", message,
		)
	}

	tests := []struct {
		name       string
		args       []string
		wantOutput string
	}{
		{"default limit", []string{directory}, "Loaded commits: 2\n"},
		{"limited", []string{"--max-count=1", directory}, "Loaded commits: 1\n"},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			var stdout, stderr bytes.Buffer
			code := run(test.args, &stdout, &stderr)

			if code != 0 {
				t.Fatalf("exit code = %d; want 0; stderr: %s", code, stderr.String())
			}
			if stdout.String() != test.wantOutput {
				t.Errorf("stdout = %q; want %q", stdout.String(), test.wantOutput)
			}
			if stderr.Len() != 0 {
				t.Errorf("unexpected stderr: %s", stderr.String())
			}
		})
	}
}

func TestRunErrors(t *testing.T) {
	directory := t.TempDir()
	missingPath := filepath.Join(directory, "missing")

	tests := []struct {
		name        string
		args        []string
		wantCode    int
		wantMessage string
	}{
		{"zero count", []string{"--max-count=0"}, 2, "must be a positive integer"},
		{"negative count", []string{"--max-count=-1"}, 2, "must be a positive integer"},
		{"invalid count", []string{"--max-count=abc"}, 2, "invalid value"},
		{"unknown flag", []string{"--unknown"}, 2, "flag provided but not defined"},
		{"extra paths", []string{"first", "second"}, 2, "expected at most one repository"},
		{"missing path", []string{missingPath}, 1, "Repository path error:"},
		{"non-git directory", []string{directory}, 1, "Could not load Git log:"},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			var stdout, stderr bytes.Buffer
			code := run(test.args, &stdout, &stderr)

			if code != test.wantCode {
				t.Errorf("exit code = %d; want %d", code, test.wantCode)
			}
			if !strings.Contains(stderr.String(), test.wantMessage) {
				t.Errorf("stderr = %q; want %q", stderr.String(), test.wantMessage)
			}
			if stdout.Len() != 0 {
				t.Errorf("unexpected stdout: %s", stdout.String())
			}
		})
	}
}
