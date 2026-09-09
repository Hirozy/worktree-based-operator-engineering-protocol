# Multi-Agent Operator Engineering

A reusable skill for coordinating Codex, Claude Code, Pi, Herdr, and other coding agents through a consistent multi-agent development and operator engineering protocol.

## Features

- Assigns an isolated Git worktree to every agent that modifies code, preventing concurrent workspace conflicts.
- Requires agents to start from the root of their assigned worktree.
- Stores `manifest.json`, `report.md`, tests, logs, benchmarks, profiles, and patches in a shared `agent-artifacts/` area outside disposable worktrees.
- Models Worktrees and Runs independently so execution history remains traceable after temporary workspaces are removed.
- Uses `Project > Campaign > Round > Variant > Run > Artifact` to organize new operator development, optimization, porting, refactoring, and validation.
- Standardizes specifications, correctness oracles, acceptance criteria, hypotheses, proposals, plans, implementations, results, audits, decisions, and final reports.

## Installation

Install from GitHub:

```bash
npx skills add https://github.com/Hirozy/multi-agent-operator-engineering
```

Install from GitCode:

```bash
npx skills add https://gitcode.com/Hirozy/multi-agent-operator-engineering.git
```

## Usage

Invoke the skill in an Agent Skills-compatible tool:

```text
$multi-agent-operator-engineering
```

Then describe the parallel development, operator implementation, optimization, porting, validation, or audit task. The skill guides the agent through worktree isolation, run and artifact recording, Campaign management, and safe cleanup.

## Files

- `SKILL.md`: Complete protocol and execution instructions.
- `README.md`: Feature overview and installation instructions.
