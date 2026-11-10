# Agent Context and Project Guide

## Project Overview
- **Name:** DevPulse
- **Languages:** Python 3.11+ & Go 1.22+
- **Goal:** Learn Python classes, decorators, data handling and Go structs/methods.
- **Considerations:** Your primary purpose is not to be a code writer, but to be a teacher and explainer for the end user. Teaching the core concept is important, but if there are significant security concerns related to the concept being taught, those should be at least summarily discussed, even though they may not be initially affect the codebase. This project will be built using Github Codespaces. The code will also be primarily run in Github Codespaces due to a lack of a local development environment.

## Current Project Status
- [x] Phase 1: Project setup and AGENTS.md and initialization
- [x] Phase 2: Core Data structures (Python implementation) - Completed
- [/] Phase 3: Classes, objects and decorators (Python) - In Progress
- [ ] Phase 4: Porting core logic to Go (Structs & Methods)
- [ ] Phase 5: JSON Persistence and Git workflow

## Session & Progress Notes
- **Verification:** Verified `python/models.py`. Typo corrected (`.resolve()`), syntax clean and models verified.
- **Phase 2 Complete:** `Commit` and `Repository` models implemented cleanly using `@dataclass` and `pathlib.Path`.
- **Phase 3 Focus:** Implementing `python/git_parser.py`:
  - Educational deep-dive into Python decorators (`@time_execution`).
  - Safe subprocess execution of `git log` without shell injection risks (`shell=False`).
  - Parsing raw output into `Commit` instances and integrating with `Repository`.

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
- **Structs:** 'Commit' and Repository fields matching the Python version
- **Pointer Recievers:** methods attached to '*Repository' to modify state.
- **Command execution:** Using 'os\exec' with Go error handling ('if err != nil').

## Rules for AI Collaborators
1. Unless given direct instructions from a user to update a file within the repo, AI and Agents should only update AGENTS.md
2. AGENTS.md should be kept up-to-date with project and process notes that covers work done or in progress.
3. Context-loss is a concern. When starting a new session, read this file first. Verify contents of this file against the codebase, and give notice to any discrepancies
4. Keep code modular, dry, clean, and educational. Provide information about best security practices as appropriate. 