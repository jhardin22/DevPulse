package main

import (
	"errors"
	"fmt"
	"os"
	"path/filepath"
)

// Commit represents an immutable Git commit record.
type Commit struct {
	Hash    string
	Author  string
	Date    string
	Message string
}

// NewCommit validates identity fields and returns a new Commit instance.
func NewCommit(hash, author, date, message string) (Commit, error) {
	if hash == "" {
		return Commit{}, errors.New("commit hash must be a non-empty string")
	}
	if author == "" {
		return Commit{}, errors.New("commit author must be a non-empty string")
	}

	return Commit{
		Hash:    hash,
		Author:  author,
		Date:    date,
		Message: message,
	}, nil
}

// Repository represents a local Git repository and its loaded commits
type Repository struct {
	RepoPath string
	Commits  []Commit
}

// NewRepository resolves and validates the given path, returning a new Repository pointer.
func NewRepository(path string) (*Repository, error) {
	if path == "" {
		return nil, errors.New("repository path must be a non-empty string")
	}

	absPath, err := filepath.Abs(path)
	if err != nil {
		return nil, fmt.Errorf("resolving repository path: %w", err)
	}

	info, err := os.Stat(absPath)
	if err != nil {
		return nil, fmt.Errorf("checking repository path %q: %w", absPath, err)
	}

	if !info.IsDir() {
		return nil, fmt.Errorf("repository path is not a directory: %s", absPath)
	}

	return &Repository{
		RepoPath: absPath,
		Commits:  make([]Commit, 0),
	}, nil
}

// AddCommit appends a new commit to the repository's commit list.
func (r *Repository) AddCommit(commit Commit) {
	r.Commits = append(r.Commits, commit)
}

// TotalCommits returns the total number of commits in the repository.
func (r *Repository) TotalCommits() int {
	return len(r.Commits)
}
