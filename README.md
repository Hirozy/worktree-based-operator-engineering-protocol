# Worktree-Based Operator Engineering Protocol

A reusable skill for coordinating Codex, Claude Code, Pi, Herdr, and other coding agents through a consistent multi-agent development and operator engineering protocol.

## Features

- Assigns an isolated Git worktree to every agent that modifies code, preventing concurrent workspace conflicts.
- Defines a formal Coordinator role for allocating worktrees, runs, permissions, and lifecycle transitions.
- Uses immutable `assignment.json` envelopes to pass exact paths, commits, inputs, outputs, and artifact locations to Workers.
- Adds Worker preflight and Coordinator `validation.json` completion handshakes.
- Maps each campaign worktree's `.agent-artifacts` entrypoint to the Campaign root while restricting execution output to the assigned Run directory.
- Makes the Coordinator request explicit consent before changing global Git excludes and otherwise use repository-local Git metadata for `.agent-artifacts`.
- Requires agents to start from the root of their assigned worktree.
- Stores `manifest.json`, `report.md`, tests, logs, benchmarks, profiles, and patches in a shared `agent-artifacts/` area outside disposable worktrees.
- Models Worktrees and Runs independently so execution history remains traceable after temporary workspaces are removed.
- Uses `Project > Campaign > Round > Variant > Run > Artifact` to organize new operator development, optimization, porting, refactoring, and validation.
- Standardizes specifications, correctness oracles, acceptance criteria, hypotheses, proposals, plans, implementations, results, audits, decisions, and final reports.

## Installation

Install from GitHub:

```bash
npx skills add https://github.com/Hirozy/worktree-based-operator-engineering-protocol
```

Install from GitCode:

```bash
npx skills add https://gitcode.com/Hirozy/worktree-based-operator-engineering-protocol.git
```

## Usage

Invoke the skill in an Agent Skills-compatible tool:

```text
$worktree-based-operator-engineering-protocol
```

Then describe the parallel development, operator implementation, optimization, porting, validation, or audit task. The skill guides the agent through worktree isolation, run and artifact recording, Campaign management, and safe cleanup.

## Files

- `SKILL.md`: Complete protocol and execution instructions.
- `templates/assignment.json`: Reusable Worker assignment envelope.
- `templates/validation.json`: Reusable Coordinator completion record.
- `schemas/assignment.schema.json`: Machine-readable assignment validation schema.
- `README.md`: Feature overview and installation instructions.
