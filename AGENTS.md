# Agent Context and Project Guide

## Project Overview
- **Name:** DevPulse
- **Languages:** Python 3.11+ & Go 1.22+ (`go/go.mod` targets `go 1.27.3`)
- **Goal:** Learn Python classes, decorators, data handling and Go structs/methods.
- **Considerations:** Your primary purpose is not to be a code writer, but to be a teacher and explainer for the end user. Teaching the core concept is important, but if there are significant security concerns related to the concept being taught, those should be at least summarily discussed, even though they may not be initially affect the codebase. This project will be built using Github Codespaces. The code will also be primarily run in Github Codespaces due to a lack of a local development environment.

## Current Project Status
- [x] Phase 1: Project setup and AGENTS.md and initialization
- [x] Phase 2: Core Data structures (Python implementation) - Completed
- [x] Phase 3: Classes, objects, decorators and CLI (Python) - First Version Complete
- [x] Phase 4: Python and Go tests - Completed; all tests pass
- [x] Phase 5: Porting core logic to Go (Structs & Methods) - Completed
- [ ] Phase 6: Author Stats, JSON Persistence, and Git Workflow

## Session & Progress Notes
- **Phase 2 Complete:** `python/models.py` defines `Commit` and `Repository` using `@dataclass` and `pathlib.Path`. Pylance found no syntax errors; focused runtime checks passed for fields, equality, frozen commits, hash and author validation, path normalization, independent commit lists, adding and counting commits, and invalid input and path errors.
- **Phase 2 limits:** `Repository` checks that the resolved path is an existing directory, not that it is a Git repository or inside an allowed directory. `Commit` validates hash and author, but does not validate date or message types.
- **Phase 3 First Version:** `python/git_parser.py` provides a timing decorator, Git subprocess integration, NUL-delimited parsing, full commit messages (`%B`), and accumulation without duplicate hashes. `python/main.py` provides a basic CLI, handles errors, and reports the number of loaded commits. Both `python python/main.py` and `python -m python.main` work from the repository root.
- **Phase 4 Complete (Test Harnesses):**
  - **Python (`unittest`):** `tests/__init__.py`, `tests/test_models.py`, `tests/test_git_parser.py`, and `tests/test_main.py` contain 20 passing tests covering model validation, `parse_records`, real-Git integration (full `%B` message bodies, `--max-count` limits, duplicate prevention), mocked invalid `max_count` checks, CLI error handling, and both CLI launch styles. `.vscode/settings.json` configures VS Code `unittest` discovery.
  - **Go (test-first):** Initialized `go/go.mod` (`github.com/jhardin22/DevPulse/go`) and wrote tests for the models and parser. The user reports that all Go tests pass.
- **Remaining Python work:** The CLI reports loaded commits up to `--max-count` (default 50), not necessarily the repository's full history. Author breakdowns and top contributors described in `README.md` are folded into Phase 6. NUL framing assumes formatted Git fields contain no NUL characters.
- **Phase 5 Go Port (Completed):** Implemented `Commit`/`Repository` structs and methods in `go/models.go`, `ParseRecords`/`ParseGitLog` in `go/parser.go` using `exec.CommandContext` with separate arguments, the CLI (`run` + `main`) in `go/main.go`, and CLI tests in `go/main_test.go`. All Go and Python tests pass.
- **Next Session — Phase 6 Plan (Author Stats, JSON Persistence & Git Workflow):**
  1. **Author Stats & Aggregation (Python + Go parity):**
     - Compute per-author commit count, percentage share of loaded commits, and first/last commit timestamps (parsed from `%aI` using `datetime.fromisoformat` in Python and `time.Parse(time.RFC3339, ...)` in Go).
     - Produce a sorted top-contributors summary (descending by commit count, alphabetical by author name on ties for deterministic output).
     - Add CLI support (e.g., `--top N`) and unit tests in both `tests/` and `go/`.
  2. **JSON Persistence / Export (Python + Go parity):**
     - Define a shared JSON report schema (repository path, total commits, author stats, and optionally commits) using `json` / `dataclasses.asdict` in Python and `encoding/json` with `json:"..."` struct tags in Go.
     - Add `--json` (print JSON to stdout) and/or `--output <path>` (write JSON to file) CLI flags.
     - **Security notes to cover:** validate `--output` paths against unintended overwrites/traversal, write files with restrictive permissions (`0600`), and avoid including author emails (`%ae`) by default to limit PII in exported artifacts.
  3. **Git Workflow:** Stage, review, and commit completed Phase 5 work on `feature/go-api-build` (or open a PR) before starting Phase 6 implementation.
- **Collaboration:** The user prefers to enter code by hand; ask before making changes and obtain explicit permission naming each file.

## Key Coding Conventions
- Keep functions small and modular.
- Document every class and struct clearly.

## Technical Specs

### Python Model Structure ('python/models.py')
- **'Commit' class:** Stores 'hash', 'author', 'date', 'message'.
- **'Repository' class:** stores 'repo_path' and 'commits' list

### Python Git Parser and Decorator ('python/git_parser.py')
- **'@time_execution' decorator:** wraps functions to log execution duration.
- **Subprocess integration:** Executes 'git log' and parses output into 'Commit' objects

### Go Port Structure ('go/')
- **Structs & Constructors:** `Commit` (`Hash`, `Author`, `Date`, `Message`) with `NewCommit(hash, author, date, message string) (Commit, error)`, and `Repository` with `NewRepository(path string) (*Repository, error)`.
- **Pointer Receivers:** `(*Repository).AddCommit(commit Commit)` and `(*Repository).TotalCommits() int`.
- **Parsing & Command execution:** `ParseRecords(rawOutput string) ([]Commit, error)` and `ParseGitLog(repo *Repository, maxCount int) ([]Commit, error)` using `os/exec` with Go error handling (`if err != nil`).

## Rules for AI Collaborators
1. Unless given direct instructions from a user to update a file within the repo, AI and Agents should only update AGENTS.md
2. AGENTS.md should be kept up-to-date with project and process notes that covers work done or in progress.
3. Context-loss is a concern. When starting a new session, read this file first. Verify contents of this file against the codebase, and give notice to any discrepancies
4. Keep code modular, dry, clean, and educational. Provide information about best security practices as appropriate. 