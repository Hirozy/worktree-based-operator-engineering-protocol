#!/usr/bin/env python3
"""Read-only v2 contract/handoff checks; no shell restriction or acceptance decision."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

from jsonschema import Draft202012Validator, FormatChecker

PACKAGE = Path(__file__).resolve().parents[1]
TERMINAL = {"completed", "failed", "cancelled"}
CHECKING_ROLES = {"test", "benchmark", "review", "audit"}


def load_json(path):
    return json.loads(Path(path).read_text())


def schema_errors(data, name):
    schema = load_json(PACKAGE / "schemas" / name)
    Draft202012Validator.check_schema(schema)
    checker = FormatChecker()
    # Some minimal jsonschema installations silently omit date-time checking.
    if checker.conforms("not-a-date", "date-time"):
        raise RuntimeError("Install jsonschema[format]; date-time checking is unavailable")
    validator = Draft202012Validator(schema, format_checker=checker)
    return [f"{'.'.join(map(str, e.absolute_path)) or '$'}: {e.message}"
            for e in sorted(validator.iter_errors(data), key=lambda e: str(list(e.absolute_path)))]


def inside(path, root):
    return path == root or root in path.parents


def normalized(value):
    return str(Path(value)) == value


def output_errors(run, relative, check_files):
    errors = []
    path = run / relative
    if not normalized(relative) or not inside(path, run) or path == run:
        errors.append(f"Invalid run-relative output: {relative}")
    if relative in {"assignment.json", "worker-start.md", "validation.json"} or relative.split('/')[0] == "protocol":
        errors.append(f"Worker output overlaps Coordinator-owned file: {relative}")
    if check_files:
        if not inside(path.resolve(), run.resolve()):
            errors.append(f"Output escapes run through a symlink: {relative}")
        if not path.exists():
            errors.append(f"Missing output: {path}")
        elif relative in {"manifest.json", "report.md"} and not path.is_file():
            errors.append(f"Required handoff document is not a file: {path}")
        elif path.is_dir():
            for child in path.rglob("*"):
                if child.is_symlink() and not inside(child.resolve(), run.resolve()):
                    errors.append(f"Evidence directory contains an escaped symlink: {child}")
    return errors


def validate_assignment(data, check_files=False):
    errors = schema_errors(data, "assignment.schema.json")
    if errors:
        return errors
    project, scope, artifacts, startup = (data[k] for k in ("project", "scope", "artifacts", "startup"))
    root, run = Path(artifacts["root_directory"]), Path(artifacts["run_directory"])
    campaign, variant = scope["campaign_id"], scope["variant_id"]
    worktree = Path(project["worktree"]) if project["worktree"] else None
    expected_campaign = root / "campaigns" / campaign if campaign else None
    expected_variant = expected_campaign / "variants" / variant if campaign and variant else None
    expected_run = (expected_variant or expected_campaign or root) / "runs" / artifacts["run_id"]

    if scope["campaign_directory"] != (str(expected_campaign) if expected_campaign else None):
        errors.append("scope.campaign_directory must match root/campaigns/campaign_id (or null)")
    if variant and not campaign:
        errors.append("A Variant requires a Campaign")
    if scope["variant_directory"] != (str(expected_variant) if expected_variant else None):
        errors.append("scope.variant_directory must match campaign/variants/variant_id (or null)")
    if run != expected_run or artifacts["run_path"] != str(expected_run.relative_to(root)):
        errors.append("run_directory/run_path must identify the canonical run under the stable project root")
    if worktree and inside(root.resolve(), worktree.resolve()):
        errors.append("Artifact root must be outside the disposable worktree")
    if worktree and inside(worktree.resolve(), root.resolve()):
        errors.append("A code worktree must not be nested inside the durable artifact root")
    if startup["working_directory"] != str(worktree or root):
        errors.append("startup.working_directory must equal the assigned worktree or artifact-only root")
    if artifacts["entrypoint"] and worktree is None:
        errors.append("A Worker without a worktree must use the absolute-path fallback (entrypoint: null)")
    for field, suffix in [("assignment_file", "assignment.json"), ("bootstrap_file", "worker-start.md"), ("protocol_file", "protocol/SKILL.md")]:
        if startup[field] != str(run / suffix):
            errors.append(f"startup.{field} must identify {run / suffix}")

    paths = list(project.values()) + list(startup.values()) + [artifacts["root_directory"], artifacts["run_directory"], artifacts["run_path"]]
    paths += [scope["campaign_directory"], scope["variant_directory"]] + data["inputs"]
    paths += data["permissions"]["additional_writable_paths"]
    for value in filter(None, paths):
        if not normalized(value):
            errors.append(f"Path must be normalized without repeated/trailing separators: {value}")
    for output in data["required_outputs"]:
        errors.extend(output_errors(run, output, False))
    for value in data["permissions"]["additional_writable_paths"]:
        path = Path(value)
        if not expected_campaign or not inside(path, expected_campaign) or path == expected_campaign or "runs" in path.relative_to(expected_campaign).parts:
            errors.append(f"Additional ownership must name an exact campaign document outside run directories: {value}")
        if expected_campaign and inside(path, expected_campaign / "summary") and not data["permissions"]["update_summary"]:
            errors.append("Writing campaign summary documents requires update_summary permission")

    text = json.dumps(data)
    if "replace-me" in text or "replace-with-" in text or "<discovered-" in text or "<full-sha>" in text:
        errors.append("Assignment contains unresolved template placeholders")

    if check_files:
        if not root.is_dir() or not run.is_dir():
            errors.append("Artifact root and assigned run directory must exist before dispatch")
        if not inside(run.resolve(), root.resolve()):
            errors.append("Run directory resolves outside the artifact root")
        for directory in (expected_campaign, expected_variant):
            if directory and (not directory.is_dir() or not inside(run.resolve(), directory.resolve())):
                errors.append(f"Run must resolve beneath its existing scope directory: {directory}")
        if not Path(startup["working_directory"]).is_dir():
            errors.append("Startup working directory does not exist")
        if artifacts["entrypoint"] and worktree:
            link = worktree / artifacts["entrypoint"]
            if not link.is_symlink() or link.resolve() != root.resolve():
                errors.append(".agent-artifacts must be a symlink to the stable project artifact root")
        for field in ("assignment_file", "bootstrap_file", "protocol_file"):
            path = Path(startup[field])
            if not path.is_file() or not inside(path.resolve(), run.resolve()):
                errors.append(f"Missing or escaped startup file: {path}")
        bootstrap = Path(startup["bootstrap_file"])
        if bootstrap.is_file():
            content = bootstrap.read_text()
            template = (PACKAGE / "templates/worker-start.md").read_text()
            placeholders = set(re.findall(r"<[A-Za-z][A-Za-z0-9-]*>", template))
            unresolved = sorted(marker for marker in placeholders if marker in content)
            if unresolved:
                errors.append("Worker startup still contains unrendered template placeholders: " + ", ".join(unresolved))
        for value in data["inputs"]:
            if not Path(value).is_file():
                errors.append(f"Missing required input file: {value}")
        for reviewed in data["reviewed_runs"]:
            path = Path(reviewed["manifest_file"])
            try:
                raw = path.read_bytes()
                previous = json.loads(raw)
                if hashlib.sha256(raw).hexdigest() != reviewed["manifest_sha256"]:
                    errors.append(f"Reviewed manifest hash changed: {path}")
                if previous.get("run_id") != reviewed["run_id"] or previous.get("status") not in TERMINAL:
                    errors.append(f"Reviewed run identity/status mismatch: {path}")
                git = previous.get("git", {})
                if data["git"]["target_commit"] and (git.get("result_commit") or git.get("target_commit")) != data["git"]["target_commit"]:
                    errors.append(f"Reviewed target evidence is for a different commit: {path}")
            except (OSError, ValueError, AttributeError) as exc:
                errors.append(f"Cannot read reviewed manifest {path}: {exc}")
    return errors


def validate_manifest(data, assignment, check_files=False):
    errors = schema_errors(data, "run-manifest.schema.json")
    if errors:
        return errors
    if data["run_id"] != assignment["artifacts"]["run_id"]:
        errors.append("Manifest run_id differs from assignment")
    if data["agent"]["role"] != assignment["role"]:
        errors.append("Manifest role differs from assignment")
    for field in ("campaign_id", "variant_id"):
        if data["scope"][field] != assignment["scope"][field]:
            errors.append(f"Manifest {field} differs from assignment")
    for field in ("branch", "base_commit", "target_commit"):
        if data["git"][field] != assignment["git"][field]:
            errors.append(f"Manifest git.{field} differs from assignment")
    if data["git"]["worktree"] != assignment["project"]["worktree"]:
        errors.append("Manifest worktree differs from assignment")
    if data["supersedes"] != assignment["supersedes"]:
        errors.append("Manifest supersedes differs from assignment")
    if data["reviewed_runs"] != [r["manifest_file"] for r in assignment["reviewed_runs"]]:
        errors.append("Manifest reviewed_runs differs from pinned assignment inputs")
    role = data["agent"]["role"]
    if role in CHECKING_ROLES and data["git"]["result_commit"] is not None:
        errors.append("Read-only checking roles must use target_commit and leave result_commit null")
    if data["status"] not in TERMINAL:
        errors.append("A submitted handoff must have terminal execution status")
    if not data["timestamps"]["created_at"] or not data["timestamps"]["finished_at"]:
        errors.append("A submitted handoff requires creation and finish timestamps")
    if data["status"] == "completed" and not data["timestamps"]["started_at"]:
        errors.append("A completed execution requires a start timestamp")

    preflight = data["preflight"]
    if data["status"] == "completed":
        expected = {
            "assignment_id": assignment["assignment_id"],
            "assignment_file": assignment["startup"]["assignment_file"],
            "protocol_file": assignment["startup"]["protocol_file"],
            "root_directory": assignment["artifacts"]["root_directory"],
            "run_directory": assignment["artifacts"]["run_directory"],
            "working_directory": assignment["startup"]["working_directory"],
            "repository": assignment["project"]["repository"],
            "worktree": assignment["project"]["worktree"],
            "campaign_id": assignment["scope"]["campaign_id"],
            "campaign_directory": assignment["scope"]["campaign_directory"],
            "variant_id": assignment["scope"]["variant_id"],
            "variant_directory": assignment["scope"]["variant_directory"],
            "run_id": assignment["artifacts"]["run_id"],
            "artifact_link_target": assignment["artifacts"]["root_directory"] if assignment["artifacts"]["entrypoint"] else None,
            "read_inputs": assignment["inputs"],
            "required_output_destinations": [str(Path(assignment["artifacts"]["run_directory"]) / p) for p in assignment["required_outputs"]],
        }
        for key, value in expected.items():
            if preflight.get(key) != value:
                errors.append(f"Missing or inconsistent startup acknowledgement: preflight.{key}")

    result = data["result"] or {}
    verdict = result.get("verdict")
    if role == "test":
        if result.get("failed", 0) > 0 and verdict != "failed":
            errors.append("Failing test cases require a failed verdict")
        if verdict == "passed" and result.get("passed", 0) == 0:
            errors.append("A test run with no passed cases cannot claim passed")
    if role in {"review", "audit"} and result.get("blocking_findings", 0) > 0 and verdict in {"valid", "valid_with_caveats"}:
        errors.append("Blocking findings cannot yield a valid audit verdict")
    if data["status"] != "completed" and verdict in {"passed", "valid", "valid_with_caveats"}:
        errors.append("Incomplete execution cannot claim successful verification")
    run = Path(assignment["artifacts"]["run_directory"])
    evidence = result.get("evidence", [])
    if not isinstance(evidence, list) or any(not isinstance(p, str) for p in evidence):
        errors.append("result.evidence must be a list of run-relative paths")
        evidence = []
    for relative in set(assignment["required_outputs"] + data["artifacts"] + evidence):
        # Required outputs are validated in the assignment; extra artifact paths
        # still need lexical validation for failed/incomplete result objects.
        if Path(relative).is_absolute() or '..' in Path(relative).parts:
            errors.append(f"Evidence path is not run-relative: {relative}")
            continue
        errors.extend(output_errors(run, relative, check_files))
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("assignment", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--check-files", action="store_true")
    args = parser.parse_args(argv)
    try:
        assignment = load_json(args.assignment)
        errors = validate_assignment(assignment, args.check_files)
        if not errors and args.check_files and args.assignment.resolve() != Path(assignment["startup"]["assignment_file"]).resolve():
            errors.append("Loaded assignment is not the declared immutable assignment file")
        if not errors and args.manifest:
            if args.check_files and args.manifest.resolve() != (Path(assignment["artifacts"]["run_directory"]) / "manifest.json").resolve():
                errors.append("Loaded manifest is not in the assigned run directory")
            errors += validate_manifest(load_json(args.manifest), assignment, args.check_files)
    except (OSError, ValueError, RuntimeError) as exc:
        errors = [str(exc)]
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1
    print("Contract checks passed; Coordinator evidence review and acceptance are still required.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
