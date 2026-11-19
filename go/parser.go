package main

import (
	"context"
	"errors"
	"fmt"
	"os/exec"
	"strings"
	"time"
)

// ParseRecords converts NUL-separated Git output into commit records.
func ParseRecords(rawOutput string) ([]Commit, error) {
	if rawOutput == "" {
		return []Commit{}, nil
	}

	if !strings.HasSuffix(rawOutput, "\x00") {
		return nil, errors.New("git output is missing its final NUL terminator")
	}

	fields := strings.Split(strings.TrimSuffix(rawOutput, "\x00"), "\x00")
	if len(fields)%4 != 0 {
		return nil, errors.New("git output must contain four fields per commit")
	}

	commits := make([]Commit, 0, len(fields)/4)
	for index := 0; index < len(fields); index += 4 {
		commit, err := NewCommit(
			fields[index],
			fields[index+1],
			fields[index+2],
			fields[index+3],
		)
		if err != nil {
			return nil, fmt.Errorf("invalid commit record: %w", err)
		}
		commits = append(commits, commit)
	}

	return commits, nil
}

// ParseGitLog loads up to maxCount commits and adds unseen commits to repo.
func ParseGitLog(repo *Repository, maxCount int) ([]Commit, error) {
	if repo == nil {
		return nil, errors.New("repository pointer must not be nil")
	}
	if maxCount < 1 {
		return nil, errors.New("maxCount must be a positive integer")
	}

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	cmd := exec.CommandContext(
		ctx,
		"git",
		"-C", repo.RepoPath,
		"log",
		"-z",
		fmt.Sprintf("--max-count=%d", maxCount),
		"--pretty=tformat:%H%x00%an%x00%aI%x00%B",
	)
	output, err := cmd.Output()
	if err != nil {
		return nil, fmt.Errorf("running git log: %w", err)
	}

	commits, err := ParseRecords(string(output))
	if err != nil {
		return nil, fmt.Errorf("parsing git log: %w", err)
	}

	existinghashes := make(map[string]struct{}, len(repo.Commits))
	for _, commit := range repo.Commits {
		existinghashes[commit.Hash] = struct{}{}
	}

	for _, commit := range commits {
		if _, exists := existinghashes[commit.Hash]; !exists {
			repo.AddCommit(commit)
			existinghashes[commit.Hash] = struct{}{}
		}
	}

	return commits, nil
}
