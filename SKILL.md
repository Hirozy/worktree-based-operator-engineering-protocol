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

For iterative Ascend operator engineering, use this hierarchy:

```text
Project
└── Campaign
    ├── Reference
    ├── Baseline, when applicable
    └── Variant
        └── Run
            └── Artifact
```

Each level answers a different question:

| Level | Required meaning |
|---|---|
| Project | What Ascend operator system or repository are we developing? |
| Campaign | What Ascend operator outcome, target, and constraints are being pursued? |
| Variant | Which concrete design, implementation, porting, or optimization hypothesis is being tested? |
| Run | Which specific agent, test, profile, or benchmark execution occurred? |
| Artifact | What raw or derived evidence did that execution produce? |

A Variant is one concrete hypothesis or implementation approach, not a Worker or an execution. A Run is one execution of that approach: implementation, test, benchmark, review, or audit. A Variant can have many Runs, each with its own assignment and exact commits. Allocate Variant IDs once across the Campaign; never reuse them. There is no Round identity, directory, or lifecycle in new campaigns. Record comparisons and milestones in summaries without grouping ownership into rounds.

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
│   └── matmul-ascend910b-v002/
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
artifact link == assignment artifacts.root_directory (the stable project artifact root)
run directory == assignment artifacts.run_directory
no other active agent owns this worktree
```

Read all applicable `AGENTS.md`, `CLAUDE.md`, repository instructions, and user constraints before editing.

Never launch a code-writing agent from the project container directory because it is not a worktree. Avoid launching it from the primary worktree when parallel agents are active.

## Coordinator Role

Use a Coordinator whenever qualifying Ascend operator work spans multiple agents, worktrees, runs, variants, or lifecycle stages. A human or deterministic program may fulfill this role, but when an Agent fulfills it, start that Agent at the project container root.

The Coordinator owns workflow control, not implementation. It must:

- Discover the actual primary repository and assigned worktree paths without requiring fixed directory names; inspect repository instructions, active worktrees, dirty state, campaign state, and current summaries before dispatch.
- Allocate collision-free task, campaign, variant, worktree, branch, and run identities.
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
  -b <dev|opt|port|refactor>/<campaign>/v<variant>-<slug> \
  "<worktrees-root-absolute-path>/<campaign-short>-v<variant>" \
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
run -> campaign/variant, when applicable
```

Worktree lifecycle:

```text
created -> active -> completed -> merged -> removed
                         └------> abandoned -> removed
```

Run execution status is `pending`, `running`, `completed`, `failed`, or `cancelled`. Execution status is separate from Coordinator validation, the test/audit verdict, and Variant decisions; see Status Machines. Archival and supersession are recorded externally and do not overwrite the terminal manifest.

A run usually outlives its worktree.

## Durable Artifact Access

Create the project artifact root and the exact assigned run directory before dispatch. Every worktree uses the same stable context mapping:

```text
<worktree>/.agent-artifacts -> <project-container>/agent-artifacts/
```

Never point this link at a Campaign, Variant, or Run, and never retarget it when a task changes. Workers can read the campaign index, reference, baseline, other variants, and historical evidence through this root. Read access does not grant ownership of those files.

The immutable assignment declares `artifacts.root_directory`, the root-relative `artifacts.run_path`, and the absolute `artifacts.run_directory`. These must identify the same location. Pass the absolute run directory to every child process that produces durable evidence; never derive output paths from cwd, a `latest` link, or a mutable "current task" pointer.

When symlinks are unavailable, set `artifacts.entrypoint` to `null` and use the absolute paths directly. An artifact-only Worker may also omit the link and worktree. Verify real paths before writing; never replace a real user directory with a symlink.

Workers remain free to use shell commands, build tools, profilers, temporary scripts, and intermediate files inside their assigned worktree or permitted scratch space. The contract governs durable deliverables, not every temporary file. Before submission, collect all evidence supporting claims into the assigned run directory, recording source and destination when copying tool output. Persistent campaign documents outside the run require explicit ownership in `permissions.additional_writable_paths`.

Do not archive a run, reuse its worktree, or switch startup pointers until the Worker and all producing child processes have stopped. The stable link alone does not make concurrent source edits safe.

Canonical paths for new executions:

```text
standalone:      agent-artifacts/runs/<run-id>/
campaign-wide:  agent-artifacts/campaigns/<campaign>/runs/<run-id>/
variant:        agent-artifacts/campaigns/<campaign>/variants/VNNN/runs/<run-id>/
```

Campaign-wide runs are for work without a particular Variant, such as aggregation or reference preparation. Every implementation, test, or audit of a particular Variant belongs under that Variant. Each run has one canonical location; indexes only reference it.

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

## Assignment Envelope Protocol

The Coordinator creates `assignment.json` in the exact run directory before dispatch. The assignment is the authoritative task contract. Use `templates/assignment.json`, populate every placeholder, and validate with `scripts/validate_contract.py`. Version 2.0 deliberately rejects the previous layout; historical assignments keep their own frozen schema.

Example (the repeated `a` SHA is illustrative; resolve a real full commit before dispatch):

```json
{
  "schema_version": "2.0",
  "assignment_id": "V001-implementation-01",
  "created_at": "2026-09-21T10:00:00+08:00",
  "coordinator": {
    "name": "coordinator",
    "run_id": "20260921-coordinator-01"
  },
  "role": "implementation",
  "objective": "Implement FP16 RMSNorm for Ascend 910B.",
  "project": {
    "container": "/projects/rmsnorm",
    "repository": "/projects/rmsnorm/ascend-ops",
    "worktree": "/projects/rmsnorm/worktrees/rmsnorm-01"
  },
  "git": {
    "branch": "dev/rmsnorm-01/v001-reference",
    "base_commit": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "target_commit": null
  },
  "scope": {
    "campaign_id": "rmsnorm-01",
    "campaign_directory": "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01",
    "variant_id": "V001",
    "variant_directory": "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/variants/V001"
  },
  "artifacts": {
    "root_directory": "/projects/rmsnorm/agent-artifacts",
    "run_id": "rmsnorm-01",
    "entrypoint": ".agent-artifacts",
    "run_path": "campaigns/rmsnorm-01/variants/V001/runs/rmsnorm-01",
    "run_directory": "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/variants/V001/runs/rmsnorm-01"
  },
  "startup": {
    "working_directory": "/projects/rmsnorm/worktrees/rmsnorm-01",
    "assignment_file": "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/variants/V001/runs/rmsnorm-01/assignment.json",
    "bootstrap_file": "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/variants/V001/runs/rmsnorm-01/worker-start.md",
    "protocol_file": "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/variants/V001/runs/rmsnorm-01/protocol/SKILL.md"
  },
  "inputs": [
    "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/README.md",
    "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/manifest.json",
    "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/reference/specification.md",
    "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/reference/api-contract.md",
    "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/reference/oracle.md",
    "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/reference/acceptance.md",
    "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/summary/status.md",
    "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/variants/V001/plan.md"
  ],
  "required_outputs": [
    "manifest.json",
    "report.md",
    "tests/correctness.json",
    "patches/final.diff"
  ],
  "verification": [
    "Record a clean result commit and test that exact commit",
    "Record unsupported shapes and unexecuted gates"
  ],
  "reviewed_runs": [],
  "permissions": {
    "modify_source": true,
    "merge": false,
    "remove_worktree": false,
    "update_summary": false,
    "additional_writable_paths": []
  },
  "supersedes": null
}
```

Assignment rules:

- Use normalized absolute host-local paths for all directories, startup files, `inputs`, and `reviewed_runs[].manifest_file`. The current implementation supports POSIX paths used on Linux and macOS. Resolve remote execution paths explicitly before dispatch.
- Discover `project.repository` from Git metadata. For code roles, `project.worktree` and `startup.working_directory` identify the assigned checkout; for artifact-only aggregation they may be the artifact root with `worktree: null`.
- `scope` records campaign and variant IDs plus their exact directories. Standalone tasks set all scope fields to `null`; campaign-wide tasks set the variant fields to `null`.
- `artifacts.entrypoint` is `.agent-artifacts` or `null`. Its target, when present, is always `artifacts.root_directory`. `run_path` is relative to that project root, not to the Campaign or Variant.
- All `required_outputs` are paths relative to this run. Do not use `..`, absolute output paths, or escaped symlinks to represent outputs owned elsewhere.
- `inputs` lists files the Worker must read, with campaign README/index, reference/acceptance files, current summary, applicable baseline, and Variant plan/preceding conclusions as appropriate to the role. The Coordinator makes them available before dispatch. Snapshot/version acceptance inputs when they could change during execution; do not silently change the assigned criteria.
- `reviewed_runs` pins each reviewed terminal manifest by absolute path, run ID, and SHA-256. Audit assignments list the test/benchmark runs whose claims they assess. A code-only review may have an empty list if its scope says so; it cannot claim to audit measurements it did not inspect.
- `git.base_commit` is the exact starting commit. Test, benchmark, review, and audit roles also require `git.target_commit`; their checkout starts at that target, which may differ from the implementation's original base. Only integration grants `merge`; read-only checking roles cannot modify implementation.
- `permissions.additional_writable_paths` lists exact additional campaign documents owned by this Worker. Read access to the full Campaign remains available. Tools and temporary experiments are not restricted by a command allowlist.
- `supersedes` is the absolute path to the prior run's manifest, or `null`. Never back-write a replacement pointer into an archived run.
- Freeze the assignment, startup file, and protocol snapshot after dispatch. Corrections require a new assignment and run; never reinterpret an old execution under a revised contract.
- Never include secrets or unredacted environment values.

### Worker Skill Bootstrap

A new Agent does not inherit the Coordinator's loaded skills or conversation. Before dispatch, the Coordinator must:

1. Copy the current `SKILL.md`, `templates/`, `schemas/`, and `scripts/` into `<run_directory>/protocol/`. Freeze this run-local snapshot; omit Git metadata, credentials, and unrelated files.
2. Render `templates/worker-start.md` as `startup.bootstrap_file`. Substitute every placeholder using the assignment: absolute contract/protocol/worktree/artifact paths, campaign/variant context, link mapping, required reading, and concrete output destinations. Use `not applicable` for absent campaign/variant/worktree/link fields. This is a view of the contract, not another source of authority.
3. Put the read-first requirement in the launch prompt, not only inside the file the Worker has yet to read:

```text
First read <absolute-assignment-file>, then <absolute-bootstrap-file>.
Before task commands or file changes, read the required instructions and inputs,
verify the directory/link mapping, and report the assignment ID, Campaign,
Variant, Run, and exact output destinations. Do not guess replacement paths.
```

4. Start the Worker in `startup.working_directory`. For manual startup, supply that exact directory and the same initial prompt. Environment variables are optional convenience only: `AGENT_ASSIGNMENT`, `AGENT_ARTIFACT_ROOT`, and `AGENT_RUN_DIR` must contain the assigned absolute paths.
5. Read the Worker's startup acknowledgement and check it against the assignment before accepting its implementation handoff. File reads and read-only preflight probes are allowed during startup; source edits and experiments wait until preflight passes.

Native skill discovery may supplement but never replace this explicit prompt. Preserve existing repository instructions; do not overwrite instruction files or global Agent settings. For reused worktrees, stop old producers first, retain the stable artifact-root link, and pass a new exact assignment path. Never find assignments by scanning for the newest run.

### Worker Preflight Handshake

The Worker first reads the assignment, bootstrap, frozen protocol, applicable repository instructions, and the required `inputs`. It must understand:

- Campaign: the shared Ascend operator goal, reference, baseline, and acceptance constraints.
- Variant (`V`): a concrete approach/hypothesis within that Campaign; IDs are campaign-wide and do not denote agents or executions.
- Run: this single assigned execution with its own role, commits, and durable evidence.
- Other Variants and their prior failures are readable context; their files are not writable without ownership.

Then verify and acknowledge actual values, not merely "I have read the protocol":

- Assignment ID, role, campaign/variant/run IDs, and the resolved assignment and protocol paths.
- Working directory, worktree root, shared Git repository identity, and branch/base or detached target commit. For artifact-only aggregation, record the worktree/Git checkout checks as `not_applicable` with a reason.
- Absolute artifact root, campaign directory, variant directory, run directory, and every required output destination.
- Actual `.agent-artifacts` link and its resolved project root, or the declared absolute-path fallback when `entrypoint` is `null`.
- Required inputs are readable, declared external destinations are writable, and no other active Worker owns the worktree.

Record these observations in `manifest.preflight` with `status`, timestamp, and resolved paths. Only then change `pending` to `running`. On mismatch, record failure using a verified run path and stop before source changes; if even that destination is untrusted, report to the Coordinator without writing through the suspect link.

### Ownership and Completion Handshake

```text
Coordinator creates frozen contract/bootstrap/protocol and pending manifest
    -> Worker reads, verifies, acknowledges, and owns active execution files
    -> Worker explores freely within assigned source/ownership boundaries
    -> Worker collects durable outputs, stops producers, and submits terminal files
    -> Coordinator checks actual files and writes validation.json
    -> Campaign decision owner considers verified tests/audits and accepts or rejects
```

The Worker may use scratch output during exploration. Before submission it must collect durable evidence, record the exact result commit, report unexecuted verification and missing outputs, and set execution status to `completed`, `failed`, or `cancelled`. `completed` means the assigned execution finished, not that tests passed or the Variant is accepted. The Worker cannot mark its own Coordinator validation passed. Only execution evidence is frozen at submission; the Coordinator subsequently adds its owned `validation.json` or termination record without altering Worker files.

`validation.json` starts as `pending`. The Coordinator checks assignment identity, startup acknowledgement, ownership, actual output paths/files, evidence-to-commit provenance, manifest/report consistency, and stopped producers. Each check becomes `passed`, `failed`, or `not_applicable` with an explanation for exemptions. Overall status is `passed` only after every required check passes; otherwise it is `needs_repair`. A missing required output does not pass merely because it was explained. Cleanup readiness may be deferred with an explicit reason before audit/integration; repeat the recovery gate before deletion.

Use the checker below for structural/path evidence, then review commands, test coverage, raw results, environment, and conclusions independently. The checker does not judge numerical correctness, audit independence, process termination, or business acceptance. This protocol is a handoff gate, not an OS sandbox or a command allowlist.

A Worker reply cannot by itself close a task. Failed validation blocks acceptance, merge, and cleanup; a Coordinator may dispatch a repair or diagnostic run to the same Worker. Freeze the submitted run; new tests, evidence recovery, corrections, and retries use new runs referencing the old manifest through `supersedes`. Do not overwrite the original evidence. Before submission, an active Worker can fill in its own missing outputs in the same run.

If the Worker crashes, confirm it and its child producers have stopped, revoke its ownership, preserve the partial files, and write a Coordinator-owned termination/validation record. Do not fabricate a Worker report or silently overwrite its unfinished manifest. Retry with a new run. No archival or cleanup while a producer might still write.

### Executable Contract Checks

Use the frozen package when checking an existing run:

```bash
uv run --no-project --with 'jsonschema[format]==4.26.0' python <protocol>/scripts/validate_contract.py <assignment.json>
uv run --no-project --with 'jsonschema[format]==4.26.0' python <protocol>/scripts/validate_contract.py <assignment.json> --check-files
uv run --no-project --with 'jsonschema[format]==4.26.0' python <protocol>/scripts/validate_contract.py <assignment.json> --manifest <manifest.json> --check-files
```

The first command validates schema and canonical path relationships. The second adds startup/link/input existence checks. The third also checks a terminal handoff's required outputs, evidence paths, reviewed manifest hashes, IDs, role, and commit consistency. Format checking is explicitly enabled and requires its optional dependencies. Templates contain intentional placeholders and are not dispatchable until populated.

## Standard Run Directory

Create the following files at their lifecycle stage: assignment/bootstrap/protocol at dispatch, manifest at creation, report at submission, and validation at Coordinator review. Optional evidence directories are created as needed:

```text
<run-id>/
├── assignment.json              # immutable dispatched input
├── worker-start.md              # rendered startup instructions
├── protocol/                    # frozen skill, schemas, templates, checker
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

Use `templates/run-manifest.json` and `schemas/run-manifest.schema.json` for dispatched Worker runs. Coordinator orchestration records are separate and need not pretend to be Worker assignments. Record ISO 8601 timestamps with timezone, exact full Git commits, and `null` for unknown results.

Example (illustrative SHAs):

```json
{
  "schema_version": "2.0",
  "run_id": "rmsnorm-01",
  "assignment_file": "assignment.json",
  "agent": {
    "name": "codex",
    "role": "implementation"
  },
  "status": "completed",
  "preflight": {
    "status": "passed",
    "assignment_id": "V001-implementation-01",
    "checked_at": "2026-09-21T10:01:00+08:00",
    "assignment_file": "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/variants/V001/runs/rmsnorm-01/assignment.json",
    "protocol_file": "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/variants/V001/runs/rmsnorm-01/protocol/SKILL.md",
    "root_directory": "/projects/rmsnorm/agent-artifacts",
    "run_directory": "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/variants/V001/runs/rmsnorm-01",
    "required_output_destinations": [
      "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/variants/V001/runs/rmsnorm-01/manifest.json",
      "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/variants/V001/runs/rmsnorm-01/report.md",
      "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/variants/V001/runs/rmsnorm-01/tests/correctness.json",
      "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/variants/V001/runs/rmsnorm-01/patches/final.diff"
    ],
    "working_directory": "/projects/rmsnorm/worktrees/rmsnorm-01",
    "repository": "/projects/rmsnorm/ascend-ops",
    "worktree": "/projects/rmsnorm/worktrees/rmsnorm-01",
    "campaign_id": "rmsnorm-01",
    "campaign_directory": "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01",
    "variant_id": "V001",
    "variant_directory": "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/variants/V001",
    "run_id": "rmsnorm-01",
    "artifact_link_target": "/projects/rmsnorm/agent-artifacts",
    "read_inputs": [
      "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/README.md",
      "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/manifest.json",
      "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/reference/specification.md",
      "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/reference/api-contract.md",
      "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/reference/oracle.md",
      "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/reference/acceptance.md",
      "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/summary/status.md",
      "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/variants/V001/plan.md"
    ]
  },
  "timestamps": {
    "created_at": "2026-09-21T10:00:00+08:00",
    "started_at": "2026-09-21T10:01:00+08:00",
    "finished_at": "2026-09-21T11:00:00+08:00"
  },
  "scope": {
    "campaign_id": "rmsnorm-01",
    "variant_id": "V001"
  },
  "git": {
    "branch": "dev/rmsnorm-01/v001-reference",
    "base_commit": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "target_commit": null,
    "worktree": "/projects/rmsnorm/worktrees/rmsnorm-01",
    "result_commit": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
  },
  "reviewed_runs": [],
  "result": null,
  "artifacts": [
    "report.md",
    "tests/correctness.json",
    "patches/final.diff"
  ],
  "supersedes": null,
  "risks": [],
  "unfinished": []
}
```

Manifest requirements:

- Keep `assignment_file` fixed as `assignment.json`; IDs, role, scope, Git starting/target commits, and worktree match that contract.
- `artifacts` and `result.evidence` contain run-relative paths. `reviewed_runs` contains absolute paths to the pinned input manifests from the assignment. References to other runs are inputs, not output files to duplicate.
- `result_commit` identifies committed implementation/integration output. Read-only test/review roles use `target_commit` and leave `result_commit` null.
- To claim verification of a result commit, test that clean commit or retain an exact source snapshot and prove it matches the recorded commit. Record command, source state, built binary provenance, environment, and raw outputs. Exploratory dirty-worktree measurements cannot silently become final-commit evidence.
- Execution timestamps and terminal status are preserved. Archival, later decisions, and supersession live in Coordinator records/indexes; do not edit old manifests to set `superseded_by` or replace outcomes with `archived`.
- Repeated execution creates a new run. Code changes invalidate applicability of earlier verdicts to the new commit; keep those verdicts as history.

## Test, Benchmark, and Audit Results

Keep three independent kinds of state:

| Layer | Values | Owner and meaning |
|---|---|---|
| Run execution | `pending`, `running`, `completed`, `failed`, `cancelled` | Worker: did this execution finish? |
| Verification result | Role-specific verdict below | Test/benchmark/audit Worker: what does the evidence establish? |
| Variant decision | `accepted`, `rejected`, `needs_revision`, `superseded`, `final`, `cancelled` | Decision owner: should this exact implementation be adopted? |

Coordinator validation (`pending`, `passed`, `needs_repair`) checks handoff completeness and provenance; it is neither a correctness verdict nor a Variant decision. A fully documented failing test can pass handoff validation while blocking Variant acceptance.

Each test or audit has its own assignment, run, manifest, report, and raw evidence under `variants/VNNN/runs/<run-id>/`. The following are role-specific manifest fragments to merge into the common model, not standalone complete manifests:

```json
{
  "agent": {"name": "tester", "role": "test"},
  "status": "completed",
  "git": {"target_commit": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", "result_commit": null},
  "result": {
    "verdict": "failed",
    "passed": 118,
    "failed": 2,
    "skipped": 4,
    "evidence": ["tests/results.json", "logs/test.log"]
  }
}
```

Test verdicts are `passed`, `failed`, or `inconclusive`. Test-case failures make the verdict `failed` even when the run completed normally. Infrastructure failure, insufficient coverage, or unavailable hardware must not imply a pass. Record `skipped` counts and gate-specific reasons; the acceptance contract decides whether skips are permissible. A test run that did not execute tests cannot pass.

Benchmark verdicts are `valid`, `invalid`, or `inconclusive` and describe measurement validity, not whether latency meets the acceptance target. Preserve metrics, units, shapes, timing methodology, environment, and raw measurements in `result` and its evidence files.

```json
{
  "agent": {"name": "auditor", "role": "audit"},
  "status": "completed",
  "git": {"target_commit": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", "result_commit": null},
  "reviewed_runs": ["/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/variants/V001/runs/test-01/manifest.json"],
  "result": {
    "verdict": "invalid",
    "blocking_findings": 1,
    "evidence": ["findings.json", "report.md"]
  }
}
```

Review/audit verdicts are `valid`, `valid_with_caveats`, `invalid`, or `inconclusive`. Each finding has a stable ID, severity, claim, code/evidence references, and required follow-up. An audit pins reviewed terminal manifests by hash in its assignment; list the same absolute manifest paths in the result manifest. The target implementation's test/benchmark evidence must match `target_commit`. Baseline/comparison runs may use different commits and must be explicitly identified as comparisons in inputs/report rather than passed off as target evidence.

Use an independent auditor for acceptance; implementation self-checks are useful evidence but do not satisfy independent audit. If that role is unavailable, record the gate as incomplete rather than silently self-approving.

Only designated owners update Variant `result.md`, `audit.md`, `decision.md`, and its manifest. Each summary identifies the exact target commit and supporting runs; retain dated prior conclusions when revising it. If two runs disagree, show the disagreement until resolved. New tests/reviews never overwrite earlier run results, and an implementation update requires fresh applicable verification before acceptance.

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

```text
agent-artifacts/campaigns/<campaign>/
├── README.md                    # goal and directory/context index
├── manifest.json                # campaign state and Variant index
├── reference/                   # specification, API, oracle, acceptance, fixtures
├── baseline/                    # only when meaningful
├── variants/
│   ├── V001/
│   │   ├── manifest.json        # ancestry, comparisons, commit, run references
│   │   ├── hypothesis.md
│   │   ├── proposal.md
│   │   ├── plan.md
│   │   ├── implementation.md
│   │   ├── result.md            # test/benchmark summary for exact commits
│   │   ├── audit.md             # independent audit summary
│   │   ├── decision.md
│   │   └── runs/
│   │       ├── <implementation-run-id>/
│   │       ├── <test-run-id>/
│   │       └── <audit-run-id>/
│   └── V002/
├── runs/                        # campaign-wide executions without a Variant
└── summary/
    ├── status.md
    ├── timeline.md
    ├── comparison.md
    ├── decisions.md
    └── final-report.md          # create only at closure
```

Create only needed directories. The Campaign README/manifest lets a Worker discover the full Campaign; startup inputs identify the subset it must read. Historical raw logs can be opened on demand. Every new Variant run is nested under its Variant. The worktree link points to the project artifact root, never the directory shown above.

`reference/` is required for every campaign. Establish `baseline/` only when comparison is meaningful. Do not invent baseline measurements for a new operator.

### Compatibility with Existing Campaigns

Version 2.0 removes Round and changes both the context-link target and canonical Variant run paths. Preserve historical assignments, runs, protocol snapshots, branches, and evidence at their original paths; use their retained schemas when interpreting them. Do not rename old records or rewrite embedded references.

Before transitioning a worktree, stop all old Workers and their producers. Use a fresh worktree when old tasks are still active; never retarget their links. New work uses v2 contracts and paths. Index older variants/runs by explicit absolute references. Reserve all existing campaign-wide V IDs before allocating new ones; if legacy IDs were only unique within rounds, assign new campaign-wide Variant IDs for continued variants and retain an explicit legacy-to-new mapping. Legacy history is not retroactively renumbered.

Variant summaries preserve dated decisions and factual corrections. Run execution evidence stays immutable after submission; campaign indexes record subsequent decisions and archival.

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
  "schema_version": "2.0",
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
  "variants": [
    "variants/V001/manifest.json",
    "variants/V002/manifest.json",
    "variants/V003/manifest.json"
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

## Variant Identity and Evolution

Allocate `V001`, `V002`, and subsequent IDs uniquely across the Campaign. A Variant owns one hypothesis or concrete approach, not a time window or a Worker. Store its descriptive mechanism in `name`; directory names remain stable `variants/VNNN/`.

Record `parent_variant` for the approach it evolved from, `base_commit` for the exact source starting point, and `comparison_variants` for alternatives it is measured against. Parentage is not the same as comparison. Use `null` for no parent and an empty list for no comparisons.

Several Variants and their runs may proceed concurrently. A retry, new measurement, or review creates a Run under the same Variant. A material change in hypothesis/design creates a new Variant assigned by the Coordinator. Refinements within the same hypothesis may produce a new commit under the existing Variant, but its earlier tests/audits do not certify that new commit.

Campaign summaries can compare any set of Variants and record dated milestones without introducing a Round ID, shared "current run", or directory move.

## Variant Record Chain

Every implemented variant must preserve this record chain:

```text
hypothesis
    -> proposal
    -> plan
    -> implementation
    -> result
    -> audit
    -> decision
```

Do not collapse these into one document. They represent distinct claims and make deviations auditable. For cancellation before implementation or a validation-only task, explicitly record unperformed stages as `not_applicable` with reasons; never fabricate implementation or results to fill a chain.

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

Use an auditor who did not implement the variant for an acceptance audit. Keep self-checks separate. Audit:

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

Every started variant must eventually have a terminal decision. `needs_revision` is an interim decision with a required follow-up, not closure:

```markdown
# Decision

Status: ACCEPTED | REJECTED | NEEDS_REVISION | SUPERSEDED | FINAL | CANCELLED

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
  "schema_version": "2.0",
  "variant_id": "V003",
  "name": "single-pass-vector-reduction",
  "status": "superseded",
  "campaign_id": "fused-rmsnorm-fp16-ascend910b",
  "branch": "dev/fused-rmsnorm-fp16-ascend910b/v003-single-pass-vector-reduction",
  "base_commit": "<full-sha>",
  "result_commit": "<full-sha>",
  "runs": [
    "runs/20260909-143012-codex-single-pass-vector-reduction-01/manifest.json",
    "runs/20260909-151820-claude-audit-01/manifest.json"
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
  "reason": "Meets the functional contract and target latency, but is superseded by a simpler accepted variant.",
  "parent_variant": "V001",
  "comparison_variants": [
    "V001",
    "V002"
  ]
}
```

All `runs` references in a v2 Variant manifest are relative to that Variant directory and identify run manifests. Legacy runs elsewhere use explicit absolute references. Narrative documents remain authoritative for reasoning. The manifest is the index for automation and dashboards.

## Summary Protocol

Treat Variant runs and campaign-wide `runs/` as evidence history and `summary/` as current campaign knowledge with append-only timeline and decision records. Only the designated aggregator updates shared summary files.

### `summary/status.md`

Keep it short enough to read first when resuming work. Include:

- Campaign state, open questions, and active Variants.
- Current best variant and exact commit.
- Reference revision, acceptance status, current selection, target, and baseline or total gain when applicable.
- Correctness and audit status.
- Current bottleneck.
- Active variants and owners.
- Next action and blocking issues.

### `summary/timeline.md`

Append dated milestones:

```text
timestamp | variant | event | commit | run | outcome
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
- Engineering journey by Variant lineage and dated milestones.
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
dev/<campaign>/vNNN-<variant-slug>
opt/<campaign>/vNNN-<variant-slug>
port/<campaign>/vNNN-<variant-slug>
refactor/<campaign>/vNNN-<variant-slug>
```

Review or audit when a branch is required:

```text
review/<campaign>/vNNN-<scope>
```

Examples:

```text
agent/codex/layernorm-tiling
agent/claude/aicore-audit
dev/fused-rmsnorm-fp16-ascend910b/v001-two-pass-reference
opt/matmul-fp16-ascend910b/v002-double-buffering
port/layernorm-ascend910b/v001-vector-core
review/matmul-fp16-ascend910b/v002-correctness
```

### Worktrees

Use a short readable name that maps to the branch:

```text
<agent>-<task-slug>
<campaign-short>-vNNN
review-<target-short>
integration-<project-short>
```

### Campaigns and Variants

```text
campaign: <operator-or-area>-<dtype-or-target>
variant:  VNNN
```

Examples:

```text
matmul-fp16-ascend910b
flash-attention-ascend910b
V002
```

Allocate Variant numbers uniquely across the Campaign; never reset or reuse them. Store the mechanism in the manifest's `name` and use `variants/VNNN/` as its directory. Never rename a Variant because priorities changed.

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

Campaign: `proposed -> active`; active campaigns may pause/resume, complete, or abort. Completion requires all started Variants to have terminal decisions or explicit cancellation. Archive via an external record that preserves the terminal outcome.

Variant: `proposed -> planned -> implementing -> testing -> auditing`. A failed test or inconclusive audit can lead to `needs_revision`, then further implementation/testing/auditing with new runs. Any nonterminal state can be cancelled or rejected with rationale. `accepted` can later become `superseded` or `final` through a dated decision. Validation-only work may omit implementation with an explicit reason. `inconclusive` is a verification verdict, not a Variant terminal decision.

Run transitions:

| From | Allowed next execution states |
|---|---|
| `pending` | `running`, `failed`, `cancelled` |
| `running` | `completed`, `failed`, `cancelled` |
| `completed`, `failed`, `cancelled` | None; preserve this outcome and create a new Run for further execution |

Coordinator validation is separate: `pending -> passed` or `pending -> needs_repair`. Repair of a submitted run gets its own execution and validation; the old record is retained. Archival and supersession are external metadata, not replacement execution statuses. When a Worker died before writing a terminal state, the Coordinator's termination record governs resumption without impersonating the Worker.

Worktree: `created -> active -> completed -> removed`, with integration or abandonment recorded when applicable. Completed test/audit worktrees need not be merged. Remove only after stopped producers, successful recovery checks, and authorized cleanup.

`accepted` means the exact Variant commit passed its decision gate; `final` means it is the selected campaign result. No status may imply success without required evidence.

## End-to-End Lifecycle

The Coordinator follows this sequence for a code-changing task:

1. Discover the actual primary repository path and existing project layout; inspect instructions, active worktrees, and dirty state.
2. Acquire Coordinator ownership for the project or campaign scope.
3. Define task, role, owner, base ref, branch, worktree, and run ID.
4. Create the branch and worktree from an explicit commit.
5. Create the durable run directory, immutable `assignment.json`, and pending `manifest.json`.
6. Add the repository-local exclude rule, link `.agent-artifacts/`, and verify both the ignore rule and assigned run path.
7. Freeze the run-local protocol snapshot, render `worker-start.md`, and start the Worker with absolute paths and an explicit prompt to read the assignment first, then the bootstrap.
8. Require the Worker preflight handshake before source modification.
9. Let the Worker implement only within the assigned scope and record deviations.
10. Let the Worker explore, test, benchmark, and profile freely; retain temporary experiments and collect durable evidence at handoff.
11. Commit intended changes, verify claims against that exact source state, stop producers, and submit `manifest.json` and `report.md`.
12. Validate the terminal run and write `validation.json`.
13. Review or audit the exact result commit from a separate worktree when required.
14. Make and record the accept, reject, supersede, or cancel decision.
15. Merge through the designated integration path when accepted.
16. Let the aggregator update shared summaries.
17. Verify recoverability, then clean up the disposable worktree and eligible branch.
18. Record archival outside the immutable run and release Coordinator ownership.

For any Ascend operator campaign, establish the reference package and Variant records after acquiring ownership in step 2 and before implementation. Establish a baseline only when the campaign type requires a meaningful comparison point.

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
| Campaign Variant index and identity allocation | Coordinator |
| Shared summary files | Single aggregator |
| Integration branch | Integrator |

Agents may read other run and variant artifacts, but must not silently rewrite them. Use a new audit, decision, correction note, or superseding run to preserve provenance.

When multiple agents need the same code base, give each a separate worktree even if they perform different tasks. For read-only jobs, prefer detached worktrees pinned to exact commits.

## Cleanup and Retention

Before removing a worktree, verify:

- Every result, including rejected work, remains recoverable through a durable Git ref/bundle or a verified recovery patch with its base and required untracked/binary content. A SHA alone is not retention.
- `manifest.json` records final status, base commit, and result commit when present.
- `report.md` records verification, risks, and unfinished work.
- Required raw test, benchmark, and profiling artifacts are durable outside the worktree.
- The decision or cancellation reason is recorded.
- No untracked user files or valuable local state remain.
- The Worker and all child producers have stopped; the worktree is not used by a live agent or process.
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

You own one run directory and, for code-based roles, one assigned Git worktree.

- First read the exact absolute `assignment.json` and `worker-start.md` supplied in the launch prompt, then the frozen protocol and required inputs before task actions.
- Treat the assignment as immutable and authoritative.
- Complete the preflight handshake before modifying source.
- Start and remain at the assigned worktree root for code operations.
- Confirm the expected branch or detached commit before editing.
- Do not modify another agent's worktree, branch, run directory, or summary files.
- Use the stable project-root `.agent-artifacts/` link to discover Campaigns and read applicable context; never retarget it.
- Use the immutable absolute `artifacts.run_directory` for durable output and pass it explicitly to child processes; collect scratch evidence before submission.
- Required run files include `<run_directory>/manifest.json` and `<run_directory>/report.md`; complete every output in the assignment.
- Store raw evidence under `logs/`, `tests/`, `benchmarks/`, `profiling/`, `patches/`, `attachments/`, or `environment/`.
- Do not commit raw execution artifacts unless explicitly requested.
- Record the base commit before work and the result commit after committing intended changes.
- Explicitly report tests or benchmarks that were not run.
- Record deviations, risks, and unfinished work.
- Do not merge, delete branches, remove worktrees, or rewrite shared summaries unless that role is explicitly assigned.
```

For Ascend operator campaign work, append:

```markdown
This run is Huawei Ascend operator work and belongs to the specified Campaign and Variant. Confirm the assigned Ascend hardware and CANN or framework target, then read the campaign README, reference package, applicable baseline, current `summary/status.md`, campaign Variant index, and the variant's preceding record documents before acting. Preserve the chain `hypothesis -> proposal -> plan -> implementation -> result -> audit -> decision`. Raw evidence belongs in the run directory; conclusions belong in the variant documents. For new development, validate specification, oracle, Ascend integration, and acceptance targets. For optimization or refactoring, also compare valid results against the original baseline and current selection. Do not invent an inapplicable baseline. Do not accept your own result unless decision authority is explicitly assigned.
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
3. For campaigns, read `README.md`, `manifest.json`, the reference package, applicable baseline documents, `summary/status.md`, `summary/decisions.md`, and the active Variant index.
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
- [ ] Worker read the contract first and acknowledged Campaign/Variant/Run identity, exact output paths, commits, link resolution, inputs, and permissions.
- [ ] The worktree link stayed at the project artifact root; child producers used the immutable absolute run directory.
- [ ] Execution status, test/audit verdict, Coordinator validation, and Variant decision remain distinct.
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
