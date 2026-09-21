# Worker Startup

You are the assigned Worker for a Huawei Ascend operator task. This bootstrap is a rendered view of the immutable assignment, not a second contract. Do not become the Coordinator or dispatch additional Workers unless explicitly authorized.

## Read first

Before task commands or file changes (read-only startup probes are allowed):

1. Read `<assignment-absolute-path>` first. Check that it names this bootstrap and your role.
2. Read `<protocol-absolute-path>` and applicable repository/Agent instructions.
3. Read every file in the assignment's `inputs`. The required context for this task is:

<required-reading-list-with-absolute-paths>

The Coordinator must put the read-first instruction and the absolute assignment/bootstrap paths in the launch prompt. Never assume this bootstrap or a locally installed Skill will be discovered automatically.

## Exact directory and link map

```text
working directory: <working-directory-absolute-path>
repository:        <repository-absolute-path>
worktree:          <worktree-absolute-path-or-not-applicable>
artifact root:     <artifact-root-absolute-path>
campaign:          <campaign-id-and-absolute-directory-or-not-applicable>
variant:           <variant-id-and-absolute-directory-or-not-applicable>
run:               <run-id-and-absolute-directory>
context link:      <absolute-link-path-to-artifact-root-or-not-applicable>
```

The context link, when present, always points to the project artifact root. It never points to a Campaign, Variant, or Run and must not change with the task. If the assignment declares `entrypoint: null`, use its absolute paths without creating a substitute link.

## Meaning and ownership

- Campaign is the shared operator goal and its reference, baseline, and acceptance criteria.
- Variant (`V001`, `V002`, etc.) is one concrete hypothesis or implementation approach. IDs are unique across the Campaign; a Variant is not a Worker or an execution.
- Run is one execution of an assigned role against exact source commits. Implementation, test, benchmark, and audit runs are separate. Retries get new run IDs.
- Read the full Campaign index and relevant sibling/history records as needed. Reading a directory does not grant write ownership.
- Temporary scripts, builds, profiling, and scratch output are allowed in the assigned worktree/permitted scratch space. Collect durable evidence into the assigned run before handoff.

## Required durable outputs

<required-output-list-with-absolute-destinations>

Pass the immutable absolute run directory explicitly to child processes. Never select output destinations from cwd, a latest link, directory scans, or another Worker's current task. Additional shared-document writes require exact ownership in the assignment.

## Preflight acknowledgement

Verify the actual working directory, Git worktree/shared repository, branch/base or target commit, artifact root/link, run directory, readable inputs, and writable destinations. Record actual resolved values and the assignment ID in `manifest.preflight`, including every required output destination. For artifact-only roles, record inapplicable checkout checks with reasons.

Report this mapping to the Coordinator and proceed only after preflight passes. If paths, links, inputs, ownership, or commits disagree, report the mismatch; do not guess replacement paths or edit source.

## Handoff

Stop child producers, collect the required evidence, and submit the manifest/report with exact commits and explicit unexecuted gates. Execution completion, test/audit verdicts, and Variant acceptance are separate. Coordinator validation is required before acceptance, merge, or cleanup; a final chat reply does not close the task.

Do not rewrite the assignment, this bootstrap, or the frozen protocol. A submitted run is preserved; further execution or repair uses a new assigned run.
