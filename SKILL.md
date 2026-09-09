---
name: multi-agent-operator-engineering
description: Coordinate Codex, Claude, Pi, Herdr, and other coding agents with isolated Git worktrees and durable external artifacts. Use for parallel agent work or multi-round operator engineering, including new operator development, optimization, hardware or backend porting, refactoring, validation, and benchmarking, with auditable specifications, hypotheses, variants, runs, evidence, decisions, and cleanup.
---

# Multi-Agent Worktree and Operator Engineering Protocol

Use this protocol to isolate concurrent code changes, preserve execution evidence after worktrees are deleted, and organize iterative operator engineering as a reproducible decision history.

An operator campaign may create a new operator, optimize an existing operator, port it to another backend or hardware target, refactor it without intended behavior changes, or validate an existing implementation. Do not assume every campaign starts with an optimized or even runnable implementation.

The protocol is agent-neutral. Apply it to Codex, Claude Code, Pi, Herdr, human developers, CI workers, benchmark workers, reviewers, and integrators.

## Core Rules

Treat the following as non-negotiable unless the user explicitly overrides them:

1. Give every concurrent code-writing agent its own Git worktree.
2. Start a code-writing agent at the root of its assigned worktree.
3. Keep persistent reports and raw execution artifacts outside disposable worktrees, under the project-level `.agent/` directory.
4. Model a worktree and a run separately: a worktree is an execution location; a run is one recorded execution.
5. Give every run a unique immutable directory. Never overwrite an earlier run with a retry.
6. Bind each completed run to exact Git commits through `manifest.json`.
7. Do not let parallel agents write the same summary file. Use one designated aggregator.
8. Preserve failed and rejected work with its evidence and decision rationale.
9. Treat worktrees as disposable and artifacts as durable.
10. Never delete a worktree until code state and required evidence are recoverable.

## Conceptual Model

For ordinary multi-agent work, use:

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

For operator engineering, use the full hierarchy:

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
| Project | What system or repository are we developing? |
| Campaign | What operator outcome, target, and constraints are being pursued? |
| Round | What bottleneck or question defines this stage? |
| Variant | Which concrete design, implementation, porting, or optimization hypothesis is being tested? |
| Run | Which specific agent, test, profile, or benchmark execution occurred? |
| Artifact | What raw or derived evidence did that execution produce? |

Do not substitute run numbers for rounds or variants. A variant may require several runs, and a round may compare several variants.

## Project Layout

Prefer a project container whose Git worktrees and durable artifacts are siblings:

```text
<project-container>/
├── repo/                         # primary worktree, usually main
├── worktrees/                    # disposable worktrees
│   ├── codex-parser-refactor/
│   ├── claude-api-review/
│   └── matmul-r003-v002/
└── .agent/                       # durable, shared, outside worktrees
    ├── runs/                     # non-campaign runs
    ├── campaigns/                # operator engineering campaigns
    ├── summary/                  # project-level aggregation
    └── registry/                 # optional machine-readable indexes
```

If the existing repository layout differs, preserve it and identify equivalent absolute paths. Never assume that the directory above the repository is writable or safe to modify; inspect first.

Do not put the shared `.agent/` store inside a disposable worktree. Do not commit raw execution artifacts unless the user explicitly requests it.

## Agent Startup Directory

Start agents according to role:

| Role | Startup location |
|---|---|
| Coder, bug fixer, refactorer | Assigned branch worktree root |
| Operator implementation agent | Assigned variant worktree root |
| Tester | Detached worktree at the exact target commit |
| Reviewer or auditor | Detached read-only worktree, or dedicated review worktree |
| Integrator | Dedicated integration worktree |
| Planner or researcher | Primary repository only when guaranteed read-only |
| Artifact aggregator | Project-level `.agent/` context; no code worktree required |

At startup, verify all of the following before modifying code:

```text
current directory == assigned worktree root
current branch or detached commit == assignment
repository root == expected repository
artifact link == assigned run directory
no other active agent owns this worktree
```

Read all applicable `AGENTS.md`, `CLAUDE.md`, repository instructions, and user constraints before editing.

Never launch a code-writing agent from the project container directory because it is not a worktree. Avoid launching it from the primary worktree when parallel agents are active.

## Git Worktree Protocol

Create a new branch and worktree from an explicit base branch or commit:

```bash
cd <project-container>/repo
git worktree add \
  -b agent/<agent>/<task-slug> \
  ../worktrees/<agent>-<task-slug> \
  <base-ref>
```

For an operator campaign variant, choose a branch prefix that matches the work:

```bash
git worktree add \
  -b <dev|opt|port|refactor>/<campaign>/r<round>-v<variant>-<slug> \
  ../worktrees/<campaign-short>-r<round>-v<variant> \
  <base-commit>
```

For immutable review or testing:

```bash
git worktree add --detach \
  ../worktrees/review-<target-short> \
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

Create the run directory before launching the agent. Expose it inside the worktree through a stable path:

```text
<worktree>/.agent-artifacts -> <project-container>/.agent/.../<run-id>
```

Use a symlink when supported. If symlinks are unavailable, provide an absolute artifact path through the agent's task instructions or an environment variable such as `AGENT_ARTIFACT_DIR`.

The path `.agent-artifacts/` is an interface, not the storage location. Verify that it resolves outside the worktree before writing. Never replace a real user directory with a symlink.

For a general task, use:

```text
.agent/runs/<run-id>/
```

For an operator campaign variant, use:

```text
.agent/campaigns/<campaign>/rounds/R<round>/V<variant>-<slug>/runs/<run-id>/
```

Do not duplicate a run in both locations. Store it at its canonical path and put only an index entry or relative reference in a project registry when global discovery is needed.

## Standard Run Directory

Every run directory must contain:

```text
<run-id>/
├── manifest.json                # required machine-readable identity and status
├── report.md                    # required human-readable outcome
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
profiling/kernel.ncu-rep
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
  "run_id": "20260909-143012-codex-parser-refactor-01",
  "task_id": "parser-refactor",
  "agent": {
    "name": "codex",
    "role": "implementation"
  },
  "status": "completed",
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
    "branch": "agent/codex/parser-refactor",
    "worktree": "worktrees/codex-parser-refactor",
    "base_commit": "<full-sha>",
    "result_commit": "<full-sha>"
  },
  "outcome": {
    "summary": "Refactored parser state handling.",
    "tests": "passed",
    "benchmarks": "not_run"
  },
  "artifacts": [
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
.agent/campaigns/<campaign>/
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
├── rounds/
│   ├── R001/
│   │   ├── README.md
│   │   ├── analysis.md
│   │   ├── V001-vectorized-load/
│   │   │   ├── manifest.json
│   │   │   ├── hypothesis.md
│   │   │   ├── proposal.md
│   │   │   ├── plan.md
│   │   │   ├── implementation.md
│   │   │   ├── result.md
│   │   │   ├── audit.md
│   │   │   ├── decision.md
│   │   │   └── runs/
│   │   │       ├── <run-id>/
│   │   │       └── <run-id>/
│   │   └── V002-cache-blocking/
│   └── R002/
└── summary/
    ├── status.md
    ├── timeline.md
    ├── comparison.md
    ├── decisions.md
    └── final-report.md
```

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

Name the operator, semantics, API, workloads, shapes, data types, layouts, backends, and supported hardware.

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
  "campaign_id": "fused-rmsnorm-fp16-sm90",
  "title": "Fused RMSNorm FP16 Operator for SM90",
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
    "variant_id": "R002-V001",
    "commit": "<full-sha>",
    "readiness": "validation"
  },
  "current_round": "R003",
  "rounds": ["R001", "R002", "R003"]
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
| `porting` | Source-backend behavior plus target-backend acceptance criteria; performance baseline when meaningful |
| `refactor` | Exact behavior/correctness baseline and performance non-regression threshold |
| `validation` | Claimed implementation commit and stated expected behavior or metrics |

When a baseline applies, create and audit it before accepting comparative claims. Record:

- Exact baseline commit and whether the worktree was clean.
- Hardware model, accelerator architecture, driver, runtime, compiler, build flags, power and clock policy.
- Operating system, relevant libraries, environment variables with secrets removed, and dependency versions.
- Input shapes, data types, layouts, distributions, seeds, warm-up count, measurement count, synchronization method, and timing method.
- Correctness oracle, tolerances, determinism requirements, and test coverage.
- P50, P90 or P95, P99, throughput, memory, and other campaign metrics.
- Raw benchmark and profiling files.

`baseline/benchmark.md` is the human-readable interpretation. `baseline/benchmark.json` is the machine-readable source. Never reconstruct missing raw baseline numbers from memory. For `new-development`, record `baseline: null` and compare the implementation with its oracle and acceptance targets until a valid internal performance baseline exists.

If the environment changes materially, either re-establish the baseline or mark cross-environment comparisons invalid.

## Round Protocol

A round represents one cycle of observation, competing attempts, and decision. It is not a single benchmark or commit.

`rounds/RNNN/analysis.md` must identify:

- Starting commit and starting variant.
- Current bottleneck and supporting evidence.
- Question this round must answer.
- Candidate mechanisms worth testing.
- Reference contract and constraints inherited from the campaign.

`rounds/RNNN/README.md` is a stage-level snapshot:

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
- Supported shapes, types, layouts, and hardware:
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
- Hardware and software compatibility.
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
  "variant_id": "R002-V001",
  "name": "single-pass-warp-reduction",
  "status": "superseded",
  "campaign_id": "fused-rmsnorm-fp16-sm90",
  "round_id": "R002",
  "branch": "dev/fused-rmsnorm-fp16-sm90/r002-v001-single-pass-warp-reduction",
  "base_commit": "<full-sha>",
  "result_commit": "<full-sha>",
  "runs": [
    "runs/20260909-143012-codex-single-pass-warp-reduction-01",
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

Narrative documents remain authoritative for reasoning. The manifest is the index for automation and dashboards.

## Summary Protocol

Treat `rounds/` as history and `summary/` as current campaign knowledge. Only the designated aggregator updates shared summary files.

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
- Supported hardware and workload range.
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

Operator campaign implementation:

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
agent/codex/parser-refactor
agent/claude/api-audit
dev/fused-rmsnorm-fp16-sm90/r001-v001-two-pass-reference
opt/matmul-fp16/r003-v002-double-buffering
port/layernorm-rocm/r002-v001-wave64
review/matmul-fp16/r003-v002-correctness
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
variant:  VNNN-<mechanism>
```

Examples:

```text
matmul-fp16
flash-attention-sm90
R003
V002-double-buffering
```

Restart variant numbering within each round. Never rename a decided round or variant merely because priorities changed.

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

Follow this sequence for a code-changing task:

1. Inspect the repository, instructions, active worktrees, and dirty state.
2. Define task, role, owner, base ref, branch, worktree, and run ID.
3. Create the branch and worktree from an explicit commit.
4. Create the durable run directory and initial `manifest.json`.
5. Link `.agent-artifacts/` to the run directory and verify resolution.
6. Start the agent from the assigned worktree root.
7. Implement only within the assigned scope and record important deviations.
8. Run relevant correctness tests, benchmarks, and profiling.
9. Save raw evidence, final patch, and environment details.
10. Commit intended code changes and record the exact result commit.
11. Complete `report.md` and finalize the run manifest.
12. Review or audit the exact result commit from a separate worktree when required.
13. Make and record the accept, reject, supersede, or cancel decision.
14. Merge through the designated integration path when accepted.
15. Let the aggregator update shared summaries.
16. Verify recoverability, then clean up the disposable worktree and eligible branch.
17. Archive the run without rewriting its evidence.

For any operator campaign, establish the reference package before step 2 and create the appropriate round and variant records before implementation. Establish a baseline only when the campaign type requires a meaningful comparison point.

## Concurrency and Ownership

Assign one writer per mutable file or namespace:

| Resource | Writer |
|---|---|
| Source files in a worktree | Assigned implementation agent |
| Run directory | Assigned run owner |
| Variant result | Result owner or designated benchmark agent |
| Variant audit | Independent auditor |
| Variant decision | Campaign decision owner |
| Round README | Round owner |
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

- Start and remain at the assigned worktree root for code operations.
- Confirm the expected branch or detached commit before editing.
- Do not modify another agent's worktree, branch, run directory, or summary files.
- Write durable execution evidence through `.agent-artifacts/`.
- Required run files are `.agent-artifacts/manifest.json` and `.agent-artifacts/report.md`.
- Store raw evidence under `logs/`, `tests/`, `benchmarks/`, `profiling/`, `patches/`, `attachments/`, or `environment/`.
- Do not commit raw execution artifacts unless explicitly requested.
- Record the base commit before work and the result commit after committing intended changes.
- Explicitly report tests or benchmarks that were not run.
- Record deviations, risks, and unfinished work.
- Do not merge, delete branches, remove worktrees, or rewrite shared summaries unless that role is explicitly assigned.
```

For operator campaign work, append:

```markdown
This run belongs to the specified Campaign, Round, and Variant. Read the campaign README, reference package, applicable baseline, current `summary/status.md`, round analysis, and the variant's preceding record documents before acting. Preserve the chain `hypothesis -> proposal -> plan -> implementation -> result -> audit -> decision`. Raw evidence belongs in the run directory; conclusions belong in the variant documents. For new development, validate specification, oracle, integration, and acceptance targets. For optimization or refactoring, also compare valid results against the original baseline and current selection. Do not invent an inapplicable baseline. Do not accept your own result unless decision authority is explicitly assigned.
```

Tool-specific launch commands may differ, but the protocol and ownership rules do not.

## Role-Specific Instructions

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

1. Locate the project container, repository, worktrees, and durable `.agent/` root.
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
- [ ] Parallel writers used separate worktrees and branches.
- [ ] Durable artifacts are outside disposable worktrees.
- [ ] Run and worktree identities are separately recorded.
- [ ] `manifest.json` is valid, final, and points to exact commits.
- [ ] `report.md` summarizes outcome, verification, risks, and handoff.
- [ ] Raw logs, tests, benchmarks, profiles, and patches use standard directories.
- [ ] Operator engineering records preserve the complete variant chain.
- [ ] Reference, oracle, and acceptance criteria are explicit.
- [ ] Baseline and current-selection comparisons are used only when applicable and methodologically valid.
- [ ] Audit and decision are recorded independently when required.
- [ ] Shared summaries were updated by the designated aggregator.
- [ ] Rejected and superseded work remains discoverable.
- [ ] Cleanup preserved all recoverable code and evidence.

## Protocol Summary

Remember these six invariants:

```text
one concurrent code-writing agent -> one worktree
one execution                     -> one run
worktree                          -> disposable code environment
.agent                            -> durable evidence and knowledge
manifest.json                     -> run-to-Git provenance
single aggregator                 -> conflict-free shared summaries
```

The purpose is not merely to keep directories tidy. It is to preserve a trustworthy, reusable record of what changed, how it was tested, why a result was believed, which ideas failed, and how later agents can continue without repeating lost work.
