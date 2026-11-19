package main

import (
	"flag"
	"fmt"
	"io"
	"os"
)

func run(args []string, stdout, stderr io.Writer) int {
	fs := flag.NewFlagSet("devpulse", flag.ContinueOnError)
	fs.SetOutput(stderr)

	maxCount := fs.Int("max-count", 50, "Maximum commits to load")
	if err := fs.Parse(args); err != nil {
		return 2
	}

	if *maxCount < 1 {
		fmt.Fprintln(stderr, "--max-count must be a positive integer")
		return 2
	}

	if fs.NArg() > 1 {
		fmt.Fprintln(stderr, "expected at most one repository")
		return 2
	}

	repoPath := "."
	if fs.NArg() == 1 {
		repoPath = fs.Arg(0)
	}

	repo, err := NewRepository(repoPath)
	if err != nil {
		fmt.Fprintf(stderr, "Repository path error: %v\n", err)
		return 1
	}

	if _, err := ParseGitLog(repo, *maxCount); err != nil {
		fmt.Fprintf(stderr, "Could not load Git log: %v\n", err)
		return 1
	}

	fmt.Fprintf(stdout, "Loaded commits: %d\n", repo.TotalCommits())
	return 0
}

func main() {
	os.Exit(run(os.Args[1:], os.Stdout, os.Stderr))
}
