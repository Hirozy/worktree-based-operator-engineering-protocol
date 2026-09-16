---
name: worktree-based-operator-engineering-protocol
description: "Coordinate Codex, Claude, Pi, Herdr, and other coding agents exclusively for Huawei Ascend (昇腾) operator engineering with a formal Coordinator role, immutable assignment envelopes, isolated Git worktrees, and durable external artifacts. Use only when a task explicitly targets operator development, optimization, porting, refactoring, validation, benchmarking, or audit for Ascend hardware or the CANN software stack. Do not use for generic multi-agent development, non-operator work, or operator tasks targeting only CUDA, ROCm, CPU, or another non-Ascend backend."
---

# Worktree-Based Operator Engineering Protocol

Use this protocol to isolate concurrent code changes, preserve execution evidence after worktrees are deleted, and organize iterative Huawei Ascend operator engineering as a reproducible decision history.

An Ascend operator campaign may create a new operator, optimize an existing Ascend implementation, port an operator from another backend to Ascend, refactor it without intended behavior changes, or validate an existing Ascend implementation. Do not assume every campaign starts with an optimized or even runnable implementation.

The protocol is agent-neutral but target-specific. Apply it to Codex, Claude Code, Pi, Herdr, human developers, CI workers, benchmark workers, reviewers, and integrators only within qualifying Ascend operator work.

## Invocation Scope

Invoke this Skill only when the requested work explicitly targets Huawei Ascend (昇腾) operator engineering. Qualifying tasks include:

- Developing operators with Ascend C, TBE, TIK, CANN custom operator APIs, or another Ascend-targeting operator toolchain.
- Integrating custom operators into CANN, `torch_npu`, MindSpore on Ascend, or an explicitly Ascend-targeted framework/runtime path.
- Optimizing, profiling, benchmarking, validating, reviewing, or auditing an operator on Ascend hardware.
- Porting an operator from CUDA, ROCm, CPU, or another backend when Ascend is the explicit destination.

Do not invoke this Skill for generic Git worktree management, ordinary multi-agent software development, application code, model-level optimization without operator implementation work, or operator work that targets only CUDA, ROCm, CPU, or another non-Ascend backend. If the hardware or backend target is unspecified, do not select this Skill automatically.

## Core Rules

Treat the following as non-negotiable unless the user explicitly overrides them:

1. Give every concurrent code-writing agent its own Git worktree.
2. Start a code-writing agent at the root of its assigned worktree.
3. Keep persistent reports and raw execution artifacts outside disposable worktrees, under the project-level `agent-artifacts/` directory.
4. Model a worktree and a run separately: a worktree is an execution location; a run is one recorded execution.
5. Give every run a unique immutable directory. Never overwrite an earlier run with a retry.
6. Bind each completed run to exact Git commits through `manifest.json`.
7. Do not let parallel agents write the same summary file. Use one designated aggregator.
8. Preserve failed and rejected work with its evidence and decision rationale.
9. Treat worktrees as disposable and artifacts as durable.
10. Never delete a worktree until code state and required evidence are recoverable.
11. Assign exactly one active Coordinator to each project or campaign coordination scope.
12. Give every dispatched Worker an immutable `assignment.json` that identifies exact paths, commits, permissions, inputs, and required outputs.
13. Keep `.agent-artifacts` out of Git by maintaining the repository-local excludes file; do not modify global Git configuration for this purpose.

## Conceptual Model

For standalone Ascend operator work that does not require a campaign, use:

```text
Task
├── Worktree
│   └── Branch
│       └── Commit
└── Run
    ├── manifest.json
    ├── report.md
    ├── tests/
    ├── logs/
    ├── benchmarks/
    └── patches/
```

For multi-round Ascend operator engineering, use the following logical hierarchy (not mandatory directory nesting):

```text
Project
└── Campaign
    ├── Reference
    ├── Baseline, when applicable
    └── Round
        └── Variant
            └── Run
                └── Artifact
```

Each level answers a different question:

| Level | Required meaning |
|---|---|
| Project | What Ascend operator system or repository are we developing? |
| Campaign | What Ascend operator outcome, target, and constraints are being pursued? |
| Round | What bottleneck or question defines this stage? |
| Variant | Which concrete design, implementation, porting, or optimization hypothesis is being tested? |
| Run | Which specific agent, test, profile, or benchmark execution occurred? |
| Artifact | What raw or derived evidence did that execution produce? |

Do not substitute run numbers for rounds or variants. A variant may require several runs, and a round may compare several variants.

The execution control flow is:

```text
Coordinator
    -> Assignment Envelope
    -> Worktree + Run
    -> Worker
    -> Completion Evidence
    -> Coordinator Validation
    -> Next Role or State Transition
```

## Project Layout

Prefer a project container whose Git worktrees and durable artifacts are siblings:

```text
<project-container>/
├── <primary-worktree-name>/       # existing primary worktree; name is discovered
├── worktrees/                    # disposable worktrees
│   ├── codex-layernorm-tiling/
│   ├── claude-aicore-review/
│   └── matmul-ascend910b-r003-v002/
└── agent-artifacts/              # durable, shared, outside worktrees
    ├── runs/                     # non-campaign runs
    └── campaigns/                # operator engineering campaigns
```

Only `campaigns/` and standalone `runs/` are default top-level artifact directories. Create directories on demand rather than empty scaffolding. Project-level `summary/` and `registry/` are optional extensions when aggregation or coordination needs them.

If the existing repository layout differs, preserve it and identify equivalent absolute paths. Never assume that the directory above the repository is writable or safe to modify; inspect first.

### Primary Worktree Discovery

The primary worktree may have any directory name. Never require a directory named `repo`, rename an existing checkout to match an example, or infer its path from a branch name or remote URL.

Before dispatch, the Coordinator must discover the actual paths:

1. Start from the user-provided repository or worktree path, or the current directory when it is inside the intended repository. If starting from a project container, inspect its existing layout to locate the intended checkout. If multiple repositories are plausible, ask the user which one to use.
2. Use Git metadata rather than directory names:

```bash
git -C "<existing-worktree-path>" rev-parse --show-toplevel
git -C "<existing-worktree-path>" worktree list --porcelain
git -C "<existing-worktree-path>" rev-parse --path-format=absolute --git-common-dir
```

3. Identify the primary worktree from the main worktree entry in Git's worktree inventory, cross-checking its shared Git metadata. The current checkout may be a linked worktree, and the primary worktree need not use a branch named `main`. Do not treat the common Git directory itself as a code worktree. A bare repository has no primary code worktree; record its actual repository path and use dedicated code worktrees.
4. Record the discovered absolute repository path in `project.repository` and the assigned execution worktree path in `project.worktree`. Resolve the project container, worktree storage root, and external artifact root independently from the existing layout. Do not construct any of these paths by appending a fixed `repo` directory name.
5. Preserve existing directory names. If the target repository cannot be identified safely, stop dispatch and request its path instead of creating or assuming a `repo` directory.

Do not put the shared `agent-artifacts/` store inside a disposable worktree. Do not commit raw execution artifacts unless the user explicitly requests it.

## Agent Startup Directory

Start agents according to role:

| Role | Startup location |
|---|---|
| Coordinator or orchestrator | Project container root; no code worktree |
| Ascend operator coder, bug fixer, refactorer | Assigned branch worktree root |
| Ascend operator implementation agent | Assigned variant worktree root |
| Tester | Detached worktree at the exact target commit |
| Reviewer or auditor | Detached read-only worktree, or dedicated review worktree |
| Integrator | Dedicated integration worktree |
| Planner or researcher | Primary repository only when guaranteed read-only |
| Artifact aggregator | Project-level `agent-artifacts/` context; no code worktree required |

At startup, verify all of the following before modifying code:

```text
current directory == assigned worktree root
current branch or detached commit == assignment
Git worktree root == assignment project.worktree
shared Git repository == assignment project.repository
artifact link == assigned campaign directory, or project artifact root for non-campaign work
run directory == assignment artifacts.run_directory
no other active agent owns this worktree
```

Read all applicable `AGENTS.md`, `CLAUDE.md`, repository instructions, and user constraints before editing.

Never launch a code-writing agent from the project container directory because it is not a worktree. Avoid launching it from the primary worktree when parallel agents are active.

## Coordinator Role

Use a Coordinator whenever qualifying Ascend operator work spans multiple agents, worktrees, runs, variants, or lifecycle stages. A human or deterministic program may fulfill this role, but when an Agent fulfills it, start that Agent at the project container root.

The Coordinator owns workflow control, not implementation. It must:

- Discover the actual primary repository and assigned worktree paths without requiring fixed directory names; inspect repository instructions, active worktrees, dirty state, campaign state, and current summaries before dispatch.
- Allocate collision-free task, campaign, round, variant, worktree, branch, and run identities.
- Resolve and record exact base commits before creating worktrees.
- Create Worker run directories, immutable assignment envelopes, initial manifests, and `.agent-artifacts` context links.
- Maintain the repository-local Git exclude rule for `.agent-artifacts` without modifying global Git configuration or committed ignore files.
- Dispatch Workers with explicit roles and stable assignment paths.
- Monitor state through manifests and reports rather than inferring progress from processes or directory names.
- Validate terminal outputs before starting audit, integration, aggregation, retry, or cleanup.
- Preserve provenance when a run fails, is cancelled, or is superseded.

The Coordinator must not:

- Modify business source code in the project container or primary worktree.
- Reuse one writable worktree for concurrent Workers.
- Rewrite a Worker's assignment after dispatch.
- Audit its own implementation result or silently approve incomplete evidence.
- Merge, delete branches, remove worktrees, or update shared summaries unless that authority is explicitly part of the assignment.
- Place secrets or credentials in prompts, assignments, manifests, or artifacts.

Allow only one active Coordinator writer for a project or campaign scope. Record ownership in `agent-artifacts/registry/coordinator.json` or an equivalent atomic lease. A second Coordinator may operate only on a disjoint scope or after an explicit ownership transfer.

The Coordinator should have its own run under `agent-artifacts/runs/` with `agent.role` set to `coordinator`. Its report records dispatches, validations, state transitions, unresolved blockers, and the final handoff. Coordinator runs do not require a code worktree.

Coordinator lifecycle:

```text
initialized -> planning -> dispatching -> monitoring -> validating
                                      ├-> replanning -> dispatching
                                      ├-> blocked
                                      └-> closing -> completed -> archived
```

## Git Worktree Protocol

Create a new branch and worktree from an explicit base branch or commit:

```bash
git -C "<primary-repository-absolute-path>" worktree add \
  -b agent/<agent>/<task-slug> \
  "<worktrees-root-absolute-path>/<agent>-<task-slug>" \
  <base-ref>
```

For an Ascend operator campaign variant, choose a branch prefix that matches the work:

```bash
git -C "<primary-repository-absolute-path>" worktree add \
  -b <dev|opt|port|refactor>/<campaign>/r<round>-v<variant>-<slug> \
  "<worktrees-root-absolute-path>/<campaign-short>-r<round>-v<variant>" \
  <base-commit>
```

For immutable review or testing:

```bash
git -C "<primary-repository-absolute-path>" worktree add --detach \
  "<worktrees-root-absolute-path>/review-<target-short>" \
  <target-commit>
```

Follow these safeguards:

- Resolve `<base-ref>` or `<target-commit>` before creating the worktree.
- Do not force the same branch into multiple worktrees.
- Never share one writable worktree between concurrent agents.
- Never change another agent's branch, worktree, files, or in-progress state.
- Do not merge automatically unless the assigned role includes integration.
- Record the base commit before implementation and the result commit after completion.
- If work must be retried, create a new run; reuse the worktree only when ownership is unchanged and doing so is explicit.

## Worktree and Run Separation

Keep the identities independent:

```text
worktree_id = where code is checked out
run_id      = one execution and its evidence
```

One worktree may host multiple sequential runs. One variant may use several worktrees over time. A reviewer run may inspect a coder's result commit from a different worktree.

Never name a run only after a worktree. Record explicit links in `manifest.json`:

```text
run -> worktree path
run -> branch
run -> base commit
run -> result commit
run -> campaign/round/variant, when applicable
```

Worktree lifecycle:

```text
created -> active -> completed -> merged -> removed
                         └------> abandoned -> removed
```

Run lifecycle:

```text
pending -> running -> completed -> archived
                  ├-> failed -> archived
                  ├-> cancelled -> archived
                  └-> superseded -> archived
```

A run usually outlives its worktree.

## Durable Artifact Access

Create the campaign and run directories before launching the agent. Expose the campaign root inside every campaign worktree through a stable path:

```text
<worktree>/.agent-artifacts -> <project-container>/agent-artifacts/campaigns/<campaign>
```

For work outside a campaign, map the same entrypoint to the project artifact root:

```text
<worktree>/.agent-artifacts -> <project-container>/agent-artifacts
```

Use a symlink when supported. If symlinks are unavailable, provide the absolute campaign or project artifact root through the agent's task instructions or an environment variable such as `AGENT_ARTIFACT_ROOT`.

The path `.agent-artifacts/` is a shared context interface, not the Worker's private run directory. Verify that it resolves outside the worktree. A Worker may read applicable campaign context but may write only within the `run_directory` declared by its assignment, except when its role explicitly grants ownership of another campaign document. Never replace a real user directory with a symlink.

### Git Ignore Hygiene

Before creating `.agent-artifacts`, the Coordinator must ensure Git ignores this exact root-level pattern:

```gitignore
/.agent-artifacts
```

Do not add a trailing slash: the worktree entrypoint is normally a symlink, and a directory-only pattern may not ignore it.

The Coordinator performs this directly through the repository-local excludes file. Preserve its existing contents and append the pattern only when absent:

```bash
exclude_file="$(git rev-parse --path-format=absolute --git-path info/exclude)"
mkdir -p "$(dirname "$exclude_file")"
touch "$exclude_file"
grep -qxF '/.agent-artifacts' "$exclude_file" ||
  printf '%s\n' '/.agent-artifacts' >> "$exclude_file"
```

This is local operational Git metadata: it is not committed and does not affect unrelated repositories. Do not use `git config --global`, modify a global excludes file, or add this entrypoint to the repository's committed `.gitignore` for this purpose.

After creating the symlink, verify it from the worktree root:

```bash
git check-ignore -v .agent-artifacts
```

If `.agent-artifacts` is already tracked, stop and report it. Do not remove it from the index or rewrite repository history without explicit authorization.

For a standalone Ascend operator task, use:

```text
agent-artifacts/runs/<run-id>/
```

For an Ascend operator campaign variant, use:

```text
agent-artifacts/campaigns/<campaign>/runs/<run-id>/
```

Do not duplicate a run in both locations. Store it at its canonical path and put only an index entry or relative reference in a project registry when global discovery is needed.

## Assignment Envelope Protocol

The Coordinator must create `assignment.json` inside the target run directory before launching a Worker. The assignment is the authoritative input contract. Prompts and environment variables carry only enough information to locate and activate that contract.

Use the retained `templates/assignment.json` and validate populated assignments against `schemas/assignment.schema.json` when those files are available.

Minimum assignment schema:

```json
{
  "schema_version": "1.1",
  "assignment_id": "R001-V001-implementation-01",
  "created_at": "2026-09-10T10:00:00+08:00",
  "coordinator": {
    "name": "herdr",
    "run_id": "20260910-095500-herdr-coordinator-01"
  },
  "role": "implementation",
  "objective": "Implement the reference FP16 RMSNorm operator for Ascend 910B.",
  "project": {
    "container": "/projects/rmsnorm",
    "repository": "/projects/rmsnorm/ascend-ops",
    "worktree": "/projects/rmsnorm/worktrees/rmsnorm-ascend910b-r001-v001"
  },
  "git": {
    "branch": "dev/rmsnorm-fp16-ascend910b/r001-v001-reference",
    "base_commit": "<full-sha>",
    "target_commit": null
  },
  "scope": {
    "campaign_id": "rmsnorm-fp16-ascend910b",
    "campaign_directory": "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-fp16-ascend910b",
    "round_id": "R001",
    "variant_id": "V001"
  },
  "artifacts": {
    "run_id": "20260910-100000-codex-implementation-01",
    "entrypoint": ".agent-artifacts",
    "run_path": "runs/20260910-100000-codex-implementation-01",
    "run_directory": "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-fp16-ascend910b/runs/20260910-100000-codex-implementation-01"
  },
  "inputs": [
    "reference/specification.md",
    "reference/api-contract.md",
    "reference/oracle.md",
    "reference/acceptance.md",
    "manifest.json",
    "summary/status.md",
    "variants/V001/plan.md"
  ],
  "required_outputs": [
    "manifest.json",
    "report.md",
    "tests/correctness.json",
    "patches/final.diff"
  ],
  "verification": [
    "Run correctness tests",
    "Record unsupported shapes",
    "Record the exact result commit"
  ],
  "permissions": {
    "modify_source": true,
    "merge": false,
    "remove_worktree": false,
    "update_summary": false
  },
  "supersedes": null
}
```

Assignment rules:

- Use absolute paths for host-local project, repository, worktree, and run locations.
- Populate `project.repository` with the discovered primary worktree or bare repository path, not a directory name imposed by an example. `project.worktree` is the assigned code checkout and may differ.
- Record the issuing Coordinator and its run ID.
- Treat `artifacts.entrypoint` as the campaign context root, not as the run directory.
- Record `artifacts.run_path` relative to the entrypoint and ensure it resolves to `artifacts.run_directory`.
- Use paths relative to the campaign directory for campaign inputs.
- Record exact full commits; do not assign a moving branch tip as review or test evidence.
- List every required output and verification gate explicitly.
- Grant only the permissions required by the assigned role.
- Never include secrets, access tokens, private keys, or unredacted environment values.
- Make `assignment.json` read-only to the Worker after dispatch. Corrections require cancellation and a new assignment or an explicitly versioned replacement.

The Coordinator passes the assignment through three compatible channels:

1. Create `<worktree>/.agent-artifacts` pointing to the campaign directory, or to the project artifact root for non-campaign work.
2. Put the exact assignment path in the launch prompt: `Read .agent-artifacts/<run-path>/assignment.json before modifying code.`
3. Optionally export `AGENT_ASSIGNMENT=.agent-artifacts/<run-path>/assignment.json`, `AGENT_ARTIFACT_ROOT=.agent-artifacts`, and `AGENT_RUN_DIR=.agent-artifacts/<run-path>` for CLI-based Workers.

Do not rely on environment inheritance alone because remote, desktop, and delegated Agent runtimes may not preserve it. Do not paste large artifacts into the prompt; pass exact file paths and commits.

### Worker Skill Bootstrap

Creating a worktree does not transfer the Coordinator's conversation, activated skills, or local skill installation to a new Agent. The artifact symlink and assignment alone do not activate this protocol. Do not assume that starting an Agent in the worktree automatically loads the skill.

Before dispatch, the Coordinator must:

1. Copy the currently used skill package (`SKILL.md`, `templates/`, and `schemas/`) into the assigned external Run directory as `protocol/`. Preserve relative references and freeze this snapshot after dispatch. Do not copy credentials, Git metadata, or unrelated files.
2. Render `templates/worker-start.md` into that Run as `worker-start.md`, replacing every placeholder with the exact worktree path and run-relative paths. This file identifies the Worker role, the protocol snapshot, and the immutable assignment. It is a bootstrap instruction, not a second assignment.
3. Start the Worker at its assigned worktree root and include this instruction in its initial prompt: `Read .agent-artifacts/<run-path>/worker-start.md and follow its startup instructions before any task action.` Substitute the actual run path; never dispatch unresolved placeholders.
4. For a manually started Agent, give the user the exact worktree directory and that same initial prompt. Starting a blank conversation is not a completed dispatch.
5. Require the Worker to read the protocol snapshot and assignment and record their resolved paths plus the assignment ID in its preflight result before editing code.

A native skill installation may be used additionally, but must not replace the explicit startup instruction or the frozen run snapshot. This fallback works through ordinary file reading and does not depend on a shared skill registry or inherited environment variables.

If zero-prompt startup is required, first verify which project instruction file the selected Agent actually discovers. A short pointer to the exact `worker-start.md` may be placed there; do not assume Codex, Claude, Pi, and Herdr share discovery rules. Preserve all existing repository instructions. Do not overwrite tracked instruction files, hide tracked edits using Git flags, or change global Agent settings. If adding a new untracked instruction file, record Coordinator ownership, exclude its exact root-relative path locally, and remove it during cleanup only if its contents remain unchanged. If safe automatic discovery cannot be established, use the explicit initial prompt instead.

When reusing a worktree for a later Run, stop the previous Worker first and update any Coordinator-owned startup pointer to the new exact Run. Never select an assignment through `latest`, a directory scan, or an ambiguous campaign-level default. If startup files are missing, unreadable, or inconsistent, stop before source edits and report the problem; do not silently fall back to an unrelated installed skill.

### Ownership Transfer

Use this single-writer sequence:

```text
Coordinator writes assignment.json and pending manifest.json
    -> Coordinator dispatches Worker
    -> Worker verifies assignment and owns manifest.json
    -> Coordinator reads only while Worker is active
    -> Worker writes terminal manifest.json and report.md
    -> Coordinator writes validation.json after Worker stops
```

The Coordinator owns `assignment.json` and `validation.json`. The active Worker owns its `manifest.json`, `report.md`, and run artifact directories. Neither may silently rewrite the other's owned files.

### Worker Preflight Handshake

Before editing, the Worker must verify:

- Current directory equals the assigned worktree root.
- Current branch or detached commit matches the assignment.
- The Git worktree root equals `project.worktree`, its shared Git metadata matches `project.repository`, and the base or target commit matches.
- `.agent-artifacts` resolves to the assigned campaign directory, or project artifact root for non-campaign work.
- The assigned `run_path` resolves to the declared external `run_directory`.
- Required input files exist and are readable.
- Requested actions fit the granted permissions.

The Worker then updates `manifest.json` from `pending` to `running` and records a `preflight` result. On mismatch, it must set the run to `failed` or `cancelled`, describe the mismatch, and avoid source changes.

### Completion Handshake

Before returning control, the Worker must:

- Set `manifest.status` to `completed`, `failed`, `cancelled`, or `superseded`.
- Record the exact result commit when source changes were intended.
- Complete `report.md` with verification, deviations, risks, unfinished work, and handoff.
- Produce every required output or explicitly record why it is absent.
- Leave shared summaries, merge state, branches, and worktree cleanup to authorized roles.

The Coordinator validates the terminal run and writes `validation.json` using `templates/validation.json` when available. Validation must cover assignment identity, role permissions, worktree and commit provenance, required outputs, verification evidence, manifest/report consistency, and cleanup readiness.

If validation fails, preserve the original run unchanged. Create a new run and assignment with `supersedes` pointing to the failed or incomplete run. Do not reopen or overwrite archived execution history.

## Standard Run Directory

Every run directory must contain:

```text
<run-id>/
├── assignment.json              # required for dispatched runs; immutable input
├── manifest.json                # required machine-readable identity and status
├── report.md                    # required human-readable outcome
├── validation.json              # Coordinator completion gate
├── logs/                        # command, build, profiler, and runtime logs
├── tests/                       # test output and correctness evidence
├── benchmarks/                  # raw benchmark data and summaries
├── patches/                     # reproducibility or recovery patches
├── profiling/                   # profiler-native files and exports
├── attachments/                 # screenshots or supporting files
└── environment/                 # environment and dependency snapshots
```

Create only needed optional directories, but use these names consistently. Keep raw data separate from conclusions.

Examples:

```text
tests/pytest.txt
tests/correctness.json
benchmarks/latency.json
benchmarks/summary.csv
logs/build.log
logs/stdout.log
profiling/msprof/
patches/final.diff
environment/system.json
```

Never store credentials, tokens, private keys, personal data, or secret environment values in artifacts.

## Run `manifest.json`

Write `manifest.json` when the run is created and update it at meaningful state transitions. Use ISO 8601 timestamps with time zone. Use `null` when an optional value is not known; do not invent values.

Minimum schema:

```json
{
  "schema_version": "1.0",
  "run_id": "20260909-143012-codex-layernorm-tiling-01",
  "assignment_file": "assignment.json",
  "task_id": "layernorm-tiling",
  "agent": {
    "name": "codex",
    "role": "implementation"
  },
  "status": "completed",
  "preflight": {
    "status": "passed",
    "checked_at": "2026-09-09T14:31:05+08:00"
  },
  "timestamps": {
    "created_at": "2026-09-09T14:30:12+08:00",
    "started_at": "2026-09-09T14:31:01+08:00",
    "finished_at": "2026-09-09T15:18:44+08:00"
  },
  "scope": {
    "campaign_id": null,
    "round_id": null,
    "variant_id": null
  },
  "git": {
    "branch": "agent/codex/layernorm-tiling",
    "worktree": "worktrees/codex-layernorm-tiling",
    "base_commit": "<full-sha>",
    "result_commit": "<full-sha>"
  },
  "outcome": {
    "summary": "Implemented Ascend LayerNorm tiling changes.",
    "tests": "passed",
    "benchmarks": "not_run"
  },
  "artifacts": [
    "assignment.json",
    "report.md",
    "tests/pytest.txt",
    "patches/final.diff"
  ],
  "supersedes": null,
  "superseded_by": null,
  "risks": [],
  "unfinished": []
}
```

Manifest requirements:

- Use paths relative to the run directory in `artifacts`.
- Ensure `assignment_file` identifies the immutable assignment used for this execution.
- Record a successful preflight before source modification.
- Prefer full commit SHAs for machine-readable fields.
- Set `result_commit` only after intended source changes are committed.
- Use `not_run`, not an implied pass, when verification was skipped.
- Set `superseded_by` on the old run and `supersedes` on the replacement run.
- Update `status` to `failed` or `cancelled` even when no code was produced.
- Keep the manifest valid JSON; put prose in `report.md`.

## Run `report.md`

Use this template:

```markdown
# Run Report

## Objective

State the assigned outcome.

## Context

- Base ref or commit:
- Branch:
- Worktree:
- Agent and role:

## Summary

Describe what happened and the final outcome.

## Changes

List source changes and relevant commit SHAs. State `None` for read-only runs.

## Verification

List each command or procedure, result, and artifact path. Explicitly state what was not run.

## Performance

Summarize benchmark results and link raw files. State `Not measured` when absent.

## Deviations

Explain deviations from the assignment or plan.

## Risks and Limitations

Record known risks, uncertainty, environment limitations, and coverage gaps.

## Unfinished Work

List remaining items or state `None`.

## Handoff

State the next owner, recommended action, and exact commit to inspect.
```

Do not paste huge logs into the report. Summarize them and reference raw artifacts.

## Operator Engineering Campaign Layout

Use one durable directory per campaign:

```text
agent-artifacts/campaigns/<campaign>/
├── README.md
├── manifest.json
├── reference/
│   ├── specification.md
│   ├── api-contract.md
│   ├── oracle.md
│   ├── acceptance.md
│   └── fixtures/
├── baseline/                     # optional; required by some campaign types
│   ├── environment.md
│   ├── benchmark.json
│   ├── benchmark.md
│   ├── correctness.json
│   └── profiling/
├── variants/
│   └── V001/
│       ├── manifest.json
│       ├── hypothesis.md
│       ├── proposal.md
│       ├── plan.md
│       ├── implementation.md
│       ├── result.md
│       ├── audit.md
│       └── decision.md
├── runs/
│   └── <run-id>/
│       ├── assignment.json
│       ├── worker-start.md
│       ├── protocol/
│       ├── manifest.json
│       ├── report.md
│       ├── tests/
│       ├── logs/
│       └── benchmarks/
└── summary/
    ├── status.md
    ├── timeline.md
    ├── comparison.md
    ├── decisions.md
    └── final-report.md
```

Variants and runs are flat within their respective campaign directories. Round is metadata, not a required parent directory. Assignments record `scope.round_id` and campaign-unique `scope.variant_id`; variant manifests record their round and campaign-relative Run references. Keep `.agent-artifacts` mapped to the Campaign root, not a Variant or Run.

Create directories only when needed. Preserve existing immutable runs and assignments at their original paths; do not migrate historical evidence. New runs use the flat layout. Validate legacy assignments using their retained protocol schema.

`reference/` is required for every campaign. `baseline/` is required only when there is a meaningful existing behavior or performance point to compare against. Do not create fake baseline measurements for a genuinely new operator.

Do not create `final-report.md` until the campaign is closing. Historical round and variant records are append-only after their decisions, except for factual corrections that are explicitly noted.

## Campaign Definition

`README.md` defines stable intent, not every experiment. Start by declaring one campaign type:

```text
new-development
optimization
porting
refactor
validation
```

Then include:

```markdown
# <Campaign Title>

## Goal

Define the operator capability or engineering outcome. Add target metrics when applicable.

## Scope

Name the Ascend operator, semantics, API, workloads, shapes, data types, layouts, CANN or framework integration path, and supported Ascend hardware.

## Constraints

Define correctness tolerance, determinism, memory, compatibility, and maintainability limits.

## Reference and Oracle

Identify the authoritative specification, behavior oracle, fixtures, and numerical tolerances.

## Baseline, If Applicable

Record the baseline commit and headline metrics.

## Success Criteria

Define required functional completeness, API compatibility, correctness, performance, portability, and audit gates.

## Exclusions

State what is intentionally out of scope.
```

Campaign `manifest.json` should include:

```json
{
  "schema_version": "1.0",
  "campaign_id": "fused-rmsnorm-fp16-ascend910b",
  "title": "Fused RMSNorm FP16 Operator for Ascend 910B",
  "campaign_type": "new-development",
  "status": "active",
  "created_at": "2026-09-09T10:00:00+08:00",
  "updated_at": "2026-09-09T15:30:00+08:00",
  "goal": {
    "outcome": "Implement a production-ready fused RMSNorm operator.",
    "primary_metric": "p50_latency_ms",
    "target": 0.08,
    "direction": "lower"
  },
  "reference": {
    "specification": "reference/specification.md",
    "api_contract": "reference/api-contract.md",
    "oracle": "reference/oracle.md",
    "acceptance": "reference/acceptance.md"
  },
  "baseline": null,
  "current_selection": {
    "variant_id": "V003",
    "commit": "<full-sha>",
    "readiness": "validation"
  },
  "current_round": "R003",
  "rounds": [
    {"round_id": "R001", "status": "closed", "variant_ids": ["V001", "V002"]},
    {"round_id": "R002", "status": "closed", "variant_ids": ["V003"]},
    {"round_id": "R003", "status": "active", "variant_ids": ["V004"]}
  ]
}
```

## Reference and Baseline Protocol

Create and review the reference package before implementing or accepting any variant. Record:

- Operator semantics, mathematical definition, data types, layouts, broadcasting, aliasing, mutability, and error behavior.
- API and ABI contract, including shapes, attributes, outputs, dispatch rules, and integration points.
- Correctness oracle, such as a framework implementation, scalar model, mathematical reference, golden vectors, or differential test target.
- Numerical tolerances and how they vary by data type, shape, accumulation mode, or hardware.
- Required fixtures, edge cases, invalid inputs, determinism requirements, and unsupported behavior.
- Functional, performance, compatibility, documentation, and integration acceptance gates.

Apply baseline requirements by campaign type:

| Campaign type | Required comparison point |
|---|---|
| `new-development` | Reference/oracle and explicit acceptance targets; baseline may be `null` |
| `optimization` | Exact existing implementation commit and audited performance baseline |
| `porting` | Source-backend behavior plus Ascend target acceptance criteria; performance baseline when meaningful |
| `refactor` | Exact behavior/correctness baseline and performance non-regression threshold |
| `validation` | Claimed implementation commit and stated expected behavior or metrics |

When a baseline applies, create and audit it before accepting comparative claims. Record:

- Exact baseline commit and whether the worktree was clean.
- Ascend hardware model and SoC version, firmware, driver, CANN toolkit/runtime/compiler, build flags, power mode, and clock policy.
- Operating system, relevant libraries, environment variables with secrets removed, and dependency versions.
- Input shapes, data types, layouts, distributions, seeds, warm-up count, measurement count, synchronization method, and timing method.
- Correctness oracle, tolerances, determinism requirements, and test coverage.
- P50, P90 or P95, P99, throughput, memory, and other campaign metrics.
- Raw benchmark and profiling files.

`baseline/benchmark.md` is the human-readable interpretation. `baseline/benchmark.json` is the machine-readable source. Never reconstruct missing raw baseline numbers from memory. For `new-development`, record `baseline: null` and compare the implementation with its oracle and acceptance targets until a valid internal performance baseline exists.

If the environment changes materially, either re-establish the baseline or mark cross-environment comparisons invalid.

## Round Protocol

A round represents one cycle of observation, competing attempts, and decision. It is not a single benchmark or commit.

Round records live in the campaign manifest's `rounds` array, including `round_id`, status, and campaign-unique `variant_ids`. They do not require a directory. The current round analysis in `summary/status.md` must identify:

- Starting commit and starting variant.
- Current bottleneck and supporting evidence.
- Question this round must answer.
- Candidate mechanisms worth testing.
- Reference contract and constraints inherited from the campaign.

Use the following section in `summary/status.md` for the active round. At closure, the aggregator appends its findings to `summary/timeline.md` and its decision to `summary/decisions.md` before replacing the current snapshot:

```markdown
# Round RNNN — <Theme>

## Starting Point

- Variant:
- Commit:
- Headline metric:

## Bottleneck

Summarize the evidence.

## Candidates

| Variant | Idea | Correctness | Result | Decision |
|---|---|---|---:|---|

## Winner

Name the selected variant and commit, or state `No winner`.

## Learned

Record reusable knowledge, including failed ideas.

## Next Question

State the bottleneck or uncertainty for the next round.
```

Close a round only after every started variant has a terminal decision or an explicit cancellation record.

## Variant Record Chain

Every variant must contain this complete chain:

```text
hypothesis
    -> proposal
    -> plan
    -> implementation
    -> result
    -> audit
    -> decision
```

Do not collapse these into one document. They represent distinct claims and make deviations auditable.

### `hypothesis.md`

Record:

- Observation and evidence.
- Suspected causal mechanism.
- Falsifiable prediction.
- Expected metric range.
- Conditions under which the hypothesis should not hold.

### `proposal.md`

Record:

- Proposed design, algorithm, implementation, port, refactor, or optimization and why it follows from the hypothesis.
- Expected benefit relative to acceptance criteria, current selection, and baseline when applicable.
- Compatibility and scope.
- Alternatives considered.
- Risks, assumptions, and rejection criteria.

Use `Hypothesis = testable belief` and `Proposal = chosen experiment`.

### `plan.md`

Record:

- Exact implementation steps.
- Files or components expected to change.
- Correctness test matrix.
- Benchmark and profiling method.
- Rollback or recovery method.
- Required agents and role boundaries.
- Completion and audit gates.

Use `Proposal = why/what` and `Plan = how`.

### `implementation.md`

Record:

- Branch, worktree, base commit, and result commit.
- Actual source changes.
- Important design choices.
- Deviations from the plan and their reasons.
- Build or environment changes.
- Known implementation limitations.

Do not claim that planned work was implemented without checking the final diff or commit.

### `result.md`

Report observed results without making the acceptance decision. Include:

```markdown
# Result

## Correctness

- Status:
- Oracle:
- Maximum error:
- Coverage:

## Specification and Integration

- API/ABI conformance:
- Supported shapes, types, layouts, and Ascend hardware:
- Framework or runtime integration:
- Unsupported or incomplete behavior:

## Performance

| Metric | Acceptance Target | Baseline, If Any | Current Selection | This Variant |
|---|---:|---:|---:|---:|

## Improvement

- Versus acceptance target:
- Versus baseline, if any:
- Versus current selection:

## Environment

State whether it matches the reference or comparison environment and reference the environment artifact.

## Raw Evidence

List run IDs and artifact paths.

## Anomalies

Record variance, regressions, and unexplained observations.
```

For optimization and refactor campaigns, compare against both the original baseline and current selection when both are valid. For new development, first report oracle conformance and acceptance-gate status, then compare performance with targets or reference implementations only when methodologically valid. State `not applicable` or `not comparable` instead of inventing a baseline.

### `audit.md`

Prefer an auditor who did not implement the variant. Audit:

- Correctness, numerical stability, determinism, undefined behavior, data races, and boundary cases.
- Test coverage and input representativeness.
- Warm-up, synchronization, iteration count, cache effects, frequency policy, variance, outliers, and statistical confidence.
- Reproducibility from the recorded commit and environment.
- Ascend hardware, firmware, driver, CANN, framework, and software compatibility.
- Memory consumption, maintainability, and operational risk.
- Whether reported tables match raw artifacts.

Use explicit verdicts:

```text
valid
valid_with_caveats
invalid
inconclusive
```

An attractive benchmark is not sufficient evidence of a valid operator. Functional completeness, specification conformance, correctness, integration, and compatibility gates remain independent.

### `decision.md`

Every started variant must end with a decision:

```markdown
# Decision

Status: ACCEPTED | REJECTED | SUPERSEDED | FINAL | CANCELLED

## Reason

Explain the decision using audited evidence.

## Selected Commit

Record the exact commit, or `None`.

## Useful Findings

Preserve what was learned, especially from failed variants.

## Action

State merge, carry-forward, rollback, or archival action.

## Follow-up

State the next question or `None`.
```

Never record only `failed`. Capture what was tried, why it did not work, which parts were useful, and what should be attempted next.

## Variant `manifest.json`

Maintain a compact machine-readable index alongside the narrative documents:

```json
{
  "schema_version": "1.0",
  "variant_id": "V003",
  "name": "single-pass-vector-reduction",
  "status": "superseded",
  "campaign_id": "fused-rmsnorm-fp16-ascend910b",
  "round_id": "R002",
  "branch": "dev/fused-rmsnorm-fp16-ascend910b/r002-v003-single-pass-vector-reduction",
  "base_commit": "<full-sha>",
  "result_commit": "<full-sha>",
  "runs": [
    "runs/20260909-143012-codex-single-pass-vector-reduction-01",
    "runs/20260909-151820-claude-audit-01"
  ],
  "requirements": {
    "specification": "passed",
    "correctness": "passed",
    "integration": "passed"
  },
  "metrics": {
    "p50_latency_ms": 0.078,
    "meets_target": true,
    "improvement_vs_baseline_percent": null
  },
  "audit_verdict": "valid",
  "decision": "superseded",
  "reason": "Meets the functional contract and target latency, but is superseded by a simpler accepted variant."
}
```

All `runs` references in a variant manifest are relative to the Campaign root, not the variant directory. Narrative documents remain authoritative for reasoning. The manifest is the index for automation and dashboards.

## Summary Protocol

Treat `variants/` and `runs/` as evidence history and `summary/` as current campaign knowledge with append-only timeline and decision records. Only the designated aggregator updates shared summary files.

### `summary/status.md`

Keep it short enough to read first when resuming work. Include:

- Campaign state and current round.
- Current best variant and exact commit.
- Reference revision, acceptance status, current selection, target, and baseline or total gain when applicable.
- Correctness and audit status.
- Current bottleneck.
- Active variants and owners.
- Next action and blocking issues.

### `summary/timeline.md`

Append dated milestones:

```text
timestamp | round | variant | event | commit | run | outcome
```

Do not rewrite history to match the current conclusion.

### `summary/comparison.md`

Maintain one normalized table across all variants:

```markdown
| Variant | Commit | Spec | Correctness | Integration | Primary Metric | vs Target | vs Baseline | Audit | Decision |
|---|---|---|---|---|---:|---:|---:|---|---|
```

Use the same units and comparison direction. Mark invalid comparisons clearly instead of coercing them into the table.

### `summary/decisions.md`

Maintain lightweight decision records:

```markdown
## DNNN — <Decision>

- Date:
- Status: accepted | rejected | superseded
- Evidence: <variant and run references>
- Reason:
- Consequence:
```

Record both adopted techniques and explicit decisions not to use a technique.

### `summary/final-report.md`

Create only when the campaign is completed or explicitly closed. Include:

- Goal, scope, constraints, and success criteria.
- Reference specification, oracle, and acceptance criteria.
- Baseline commit, environment, and measurements when applicable.
- Engineering journey by round.
- Key accepted and rejected hypotheses.
- Final implementation and exact commit.
- Final correctness and audited performance.
- Supported Ascend hardware and workload range.
- Known risks and limitations.
- Reproduction steps and artifact index.
- Unresolved questions and future directions.

The final report is the campaign's main handoff document; it does not replace raw evidence.

## Naming Conventions

Use lowercase ASCII kebab-case for slugs. Avoid spaces, mutable labels such as `latest`, and names such as `final2`.

### Branches

General implementation:

```text
agent/<agent>/<task-slug>
```

Ascend operator campaign implementation:

```text
dev/<campaign>/rNNN-vNNN-<variant-slug>
opt/<campaign>/rNNN-vNNN-<variant-slug>
port/<campaign>/rNNN-vNNN-<variant-slug>
refactor/<campaign>/rNNN-vNNN-<variant-slug>
```

Review or audit when a branch is required:

```text
review/<campaign>/rNNN-vNNN-<scope>
```

Examples:

```text
agent/codex/layernorm-tiling
agent/claude/aicore-audit
dev/fused-rmsnorm-fp16-ascend910b/r001-v001-two-pass-reference
opt/matmul-fp16-ascend910b/r003-v002-double-buffering
port/layernorm-ascend910b/r002-v001-vector-core
review/matmul-fp16-ascend910b/r003-v002-correctness
```

### Worktrees

Use a short readable name that maps to the branch:

```text
<agent>-<task-slug>
<campaign-short>-rNNN-vNNN
review-<target-short>
integration-<project-short>
```

### Campaigns, Rounds, and Variants

```text
campaign: <operator-or-area>-<dtype-or-target>
round:    RNNN
variant:  VNNN
```

Examples:

```text
matmul-fp16-ascend910b
flash-attention-ascend910b
R003
V002
```

Allocate variant numbers uniquely across the Campaign; never restart numbering in a new Round. Store the mechanism in the manifest's `name` and use `variants/VNNN/` as its directory. Never rename a decided round or variant merely because priorities changed.

### Runs

Use sortable, collision-resistant IDs:

```text
YYYYMMDD-HHMMSS-<agent>-<task-or-role>-NN
```

Examples:

```text
20260909-143012-codex-double-buffering-01
20260909-151820-claude-audit-01
20260909-160405-pi-benchmark-01
```

If runs can be created concurrently across hosts, append a short host or random suffix.

### Artifacts

Use stable semantic names:

```text
manifest.json
report.md
correctness.json
benchmark.json
benchmark.md
environment.json
stdout.log
build.log
final.diff
```

Encode variant identity in the directory, not repeatedly in every filename.

## Status Machines

Use only defined status values in manifests.

Campaign:

```text
proposed -> active -> paused -> active
                  -> completed -> archived
                  -> aborted -> archived
```

Round:

```text
planned -> active -> decided -> closed
                  -> cancelled
```

Variant:

```text
proposed -> planned -> implementing -> testing -> auditing
                                             ├-> accepted -> superseded
                                             │           -> final
                                             ├-> rejected
                                             ├-> cancelled
                                             └-> inconclusive
```

Run:

```text
pending -> running -> completed -> archived
                  ├-> failed -> archived
                  ├-> cancelled -> archived
                  └-> superseded -> archived
```

Worktree:

```text
created -> active -> completed -> merged -> removed
                         └-> abandoned -> removed
```

Do not skip directly to a success state without the required evidence. `accepted` means the variant passed its decision gate; `final` means it is the selected campaign result.

## End-to-End Lifecycle

The Coordinator follows this sequence for a code-changing task:

1. Discover the actual primary repository path and existing project layout; inspect instructions, active worktrees, and dirty state.
2. Acquire Coordinator ownership for the project or campaign scope.
3. Define task, role, owner, base ref, branch, worktree, and run ID.
4. Create the branch and worktree from an explicit commit.
5. Create the durable run directory, immutable `assignment.json`, and pending `manifest.json`.
6. Add the repository-local exclude rule, link `.agent-artifacts/`, and verify both the ignore rule and assigned run path.
7. Freeze the run-local protocol snapshot, render `worker-start.md`, and start the Worker from its assigned worktree root with an explicit prompt to read that bootstrap.
8. Require the Worker preflight handshake before source modification.
9. Let the Worker implement only within the assigned scope and record deviations.
10. Let the Worker run correctness tests, benchmarks, and profiling and save raw evidence.
11. Require the Worker to commit intended changes and finalize `manifest.json` and `report.md`.
12. Validate the terminal run and write `validation.json`.
13. Review or audit the exact result commit from a separate worktree when required.
14. Make and record the accept, reject, supersede, or cancel decision.
15. Merge through the designated integration path when accepted.
16. Let the aggregator update shared summaries.
17. Verify recoverability, then clean up the disposable worktree and eligible branch.
18. Archive the run without rewriting its evidence and release Coordinator ownership.

For any Ascend operator campaign, establish the reference package before step 2 and create the appropriate round and variant records before implementation. Establish a baseline only when the campaign type requires a meaningful comparison point.

## Concurrency and Ownership

Assign one writer per mutable file or namespace:

| Resource | Writer |
|---|---|
| Coordinator registry and lease | Active Coordinator |
| Worker `assignment.json` | Coordinator; immutable after dispatch |
| Active Worker `manifest.json` and `report.md` | Assigned Worker |
| Run `validation.json` | Coordinator after Worker termination |
| Source files in a worktree | Assigned implementation agent |
| Run directory | Assigned run owner |
| Variant result | Result owner or designated benchmark agent |
| Variant audit | Independent auditor |
| Variant decision | Campaign decision owner |
| Round metadata in campaign manifest | Coordinator |
| Round analysis and closure records in summary | Single aggregator using round-owner evidence |
| Shared summary files | Single aggregator |
| Integration branch | Integrator |

Agents may read other run and variant artifacts, but must not silently rewrite them. Use a new audit, decision, correction note, or superseding run to preserve provenance.

When multiple agents need the same code base, give each a separate worktree even if they perform different tasks. For read-only jobs, prefer detached worktrees pinned to exact commits.

## Cleanup and Retention

Before removing a worktree, verify:

- Intended changes are committed, or an explicit recovery patch is stored.
- `manifest.json` records final status, base commit, and result commit when present.
- `report.md` records verification, risks, and unfinished work.
- Required raw test, benchmark, and profiling artifacts are durable outside the worktree.
- The decision or cancellation reason is recorded.
- No untracked user files or valuable local state remain.
- The worktree is not the current directory of a live agent or process.
- Accepted work is merged or its exact commit remains reachable.

Then remove the worktree with Git's worktree command. Prune stale metadata only after inspecting it. Delete a branch only when it is merged, rejected with preserved evidence, or explicitly authorized. Never use destructive reset or forced deletion as routine cleanup.

Retention rules:

- Keep manifests, reports, decisions, benchmark summaries, and reproducibility metadata long-term.
- Keep failed and rejected variant knowledge long-term.
- Keep raw evidence at least through audit and campaign closure.
- Apply an explicit project retention policy to very large profiler traces or logs.
- If raw files are expired, retain checksums, metadata, summaries, and the deletion record.
- Do not mutate historical run contents after archival; append a correction record instead.
- A `latest` symlink or index may point to the newest run, but it must never replace immutable history.

## Agent-Neutral Assignment Block

Include or adapt this block when dispatching Codex, Claude, Pi, Herdr, or another agent:

```markdown
## Worktree and Artifact Protocol

You own exactly one assigned Git worktree and one run directory.

- Read the exact `worker-start.md` supplied in the launch prompt, then its run-local protocol snapshot and `.agent-artifacts/<run-path>/assignment.json` before taking any task action.
- Treat the assignment as immutable and authoritative.
- Complete the preflight handshake before modifying source.
- Start and remain at the assigned worktree root for code operations.
- Confirm the expected branch or detached commit before editing.
- Do not modify another agent's worktree, branch, run directory, or summary files.
- Use `.agent-artifacts/` to read applicable campaign context.
- Write durable execution evidence only through the assigned `.agent-artifacts/<run-path>/` directory.
- Required run files are `.agent-artifacts/<run-path>/manifest.json` and `.agent-artifacts/<run-path>/report.md`.
- Store raw evidence under `logs/`, `tests/`, `benchmarks/`, `profiling/`, `patches/`, `attachments/`, or `environment/`.
- Do not commit raw execution artifacts unless explicitly requested.
- Record the base commit before work and the result commit after committing intended changes.
- Explicitly report tests or benchmarks that were not run.
- Record deviations, risks, and unfinished work.
- Do not merge, delete branches, remove worktrees, or rewrite shared summaries unless that role is explicitly assigned.
```

For Ascend operator campaign work, append:

```markdown
This run is Huawei Ascend operator work and belongs to the specified Campaign, Round, and Variant. Confirm the assigned Ascend hardware and CANN or framework target, then read the campaign README, reference package, applicable baseline, current `summary/status.md`, round analysis, and the variant's preceding record documents before acting. Preserve the chain `hypothesis -> proposal -> plan -> implementation -> result -> audit -> decision`. Raw evidence belongs in the run directory; conclusions belong in the variant documents. For new development, validate specification, oracle, Ascend integration, and acceptance targets. For optimization or refactoring, also compare valid results against the original baseline and current selection. Do not invent an inapplicable baseline. Do not accept your own result unless decision authority is explicitly assigned.
```

Tool-specific launch commands may differ, but the protocol and ownership rules do not.

## Role-Specific Instructions

### Coordinator Agent

- Start at the project container root and never edit business source there.
- Acquire exclusive coordination ownership before allocating mutable identities.
- Create exact assignments, worktrees, runs, artifact links, and pending manifests.
- Prepare frozen run-local protocol snapshots and startup files; dispatch Workers with explicit startup paths rather than assuming skill inheritance.
- Treat active Worker run contents as read-only.
- Validate terminal evidence and write `validation.json` before advancing state.
- Create a new superseding run for retries; never rewrite execution history.
- Delegate implementation, independent audit, integration, aggregation, and cleanup according to explicit permissions.

### Implementation Agent

- Edit only in the assigned worktree.
- Follow the plan or document deviations.
- Produce a committed result when source changes are intended.
- Do not self-approve benchmark validity.

### Test or Benchmark Agent

- Pin work to an exact commit.
- Preserve full commands, environment, raw outputs, and failures.
- Do not alter implementation merely to make a test pass unless reassigned as an implementation run.

### Reviewer or Audit Agent

- Review the exact result commit, not a moving branch tip.
- Validate reported claims against artifacts and code.
- Separate correctness, methodology, reproducibility, and maintainability findings.
- Record `inconclusive` when evidence is insufficient.

### Integrator

- Merge only accepted commits.
- Re-run integration-level checks when variants interact.
- Record conflict resolution and resulting merge commit.
- Never use an implementation agent's worktree as the integration worktree.

### Aggregator

- Read manifests and finalized reports; do not infer success from directory names.
- Normalize metrics only when units and environments are comparable.
- Update project or campaign summaries as the sole writer.
- Preserve links to exact variants, runs, artifacts, and commits.

## Resuming Existing Work

When joining an existing project or campaign:

1. Rediscover the actual project container, primary repository, worktrees, and durable `agent-artifacts/` root from the existing layout and Git metadata, without assuming fixed directory names.
2. Read repository instructions and inspect active worktrees.
3. For campaigns, read `README.md`, `manifest.json`, the reference package, applicable baseline documents, `summary/status.md`, `summary/decisions.md`, and the current round.
4. Inspect the target variant and all prior documents in its record chain.
5. Read relevant run manifests and reports; open raw artifacts only as needed.
6. Verify branch and commit identities before continuing.
7. Create a new run for new execution. Never append new execution output to an archived run.

If records conflict, treat exact commits and raw evidence as primary facts, flag the inconsistency, and ask the responsible owner or create a correction record.

## Completion Checklist

Do not report completion until all applicable checks pass:

- [ ] Agent operated in the assigned worktree root.
- [ ] Exactly one Coordinator owned the project or campaign coordination scope.
- [ ] Every dispatched run retained its immutable `assignment.json`.
- [ ] Worker preflight verified paths, commits, artifact resolution, inputs, and permissions.
- [ ] Parallel writers used separate worktrees and branches.
- [ ] Repository-local Git metadata ignores `.agent-artifacts`; no global Git configuration was changed.
- [ ] Durable artifacts are outside disposable worktrees.
- [ ] Run and worktree identities are separately recorded.
- [ ] `manifest.json` is valid, final, and points to exact commits.
- [ ] `report.md` summarizes outcome, verification, risks, and handoff.
- [ ] Coordinator `validation.json` records the completion-gate result.
- [ ] Raw logs, tests, benchmarks, profiles, and patches use standard directories.
- [ ] Operator engineering records preserve the complete variant chain.
- [ ] Reference, oracle, and acceptance criteria are explicit.
- [ ] Baseline and current-selection comparisons are used only when applicable and methodologically valid.
- [ ] Audit and decision are recorded independently when required.
- [ ] Shared summaries were updated by the designated aggregator.
- [ ] Rejected and superseded work remains discoverable.
- [ ] Cleanup preserved all recoverable code and evidence.

## Protocol Summary

Remember these eight invariants:

```text
one concurrent code-writing agent -> one worktree
one execution                     -> one run
one coordination scope            -> one active Coordinator
one dispatched Worker             -> one immutable assignment
worktree                          -> disposable code environment
agent-artifacts                   -> durable evidence and knowledge
manifest.json                     -> run-to-Git provenance
single aggregator                 -> conflict-free shared summaries
```

The purpose is not merely to keep directories tidy. It is to preserve a trustworthy, reusable record of what changed, how it was tested, why a result was believed, which ideas failed, and how later agents can continue without repeating lost work.
