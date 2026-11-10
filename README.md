# DevPulse 🚀

A github project to learn git by building an app to get git stats with git

DevPulse is a lightweight, dual-implementation command-line interface (CLI) tool designed to inspect local Git repositories, parse commit histories, and aggregate developer statistics. 

Built side-by-side in **Python** and **Go**, DevPulse serves as a practical software engineering sandbox to compare object-oriented design patterns with procedural/struct-based architecture.

---

## Project Concept & Scope

The primary objective of DevPulse is educational: bridging the gap between basic syntax and real-world project implementation. It reads raw Git log data using operating system subprocesses, structures that data into custom data models, and outputs clean analytics.

### In-Scope Features
- **Local Repository Inspection:** Scans any valid local Git repository via file path or current working directory.
- **Commit Parsing:** Extracts commit hashes, author names, dates, and commit messages.
- **Statistical Aggregation:** Computes total commit counts, breaks down activity by author, and identifies top contributors.
- **Dual-Language Implementation:** Complete functional parity between Python and Go implementations.
- **Context-Resilient Documentation (`AGENTS.md`):** Maintains persistent state to allow seamless AI-assisted development across disconnected context windows.

### Out-of-Scope (Explicitly Excluded)
- Remote GitHub/GitLab API integrations (DevPulse strictly inspects *local* `.git` directories).
- Web servers, graphical user interfaces (GUIs), or database persistence (output is printed directly to the terminal).
- Complex branch graph visualizers (focus remains on linear commit stream analytics)