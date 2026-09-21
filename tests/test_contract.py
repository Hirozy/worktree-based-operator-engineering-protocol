import hashlib
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("validator", ROOT / "scripts/validate_contract.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "agent-artifacts"
        self.worktree = self.base / "worktrees/worker"
        self.worktree.mkdir(parents=True)
        self.root.mkdir()
        (self.worktree / ".agent-artifacts").symlink_to(self.root, target_is_directory=True)
        self.a = json.loads((ROOT / "templates/assignment.json").read_text())
        self.a.update(assignment_id="assignment-01", objective="Test protocol")
        self.a["coordinator"] = {"name": "coordinator", "run_id": "coord-01"}
        self.a["project"] = {"container": str(self.base), "repository": str(self.base / "source"), "worktree": str(self.worktree)}
        self.a["git"] = {"branch": "dev/campaign/v001", "base_commit": "a" * 40, "target_commit": None}
        self.place_run("campaign", "V001", "implementation-01")

    def place_run(self, campaign, variant, run_id):
        cdir = self.root / "campaigns" / campaign if campaign else None
        vdir = cdir / "variants" / variant if variant else None
        self.run = (vdir or cdir or self.root) / "runs" / run_id
        self.run.mkdir(parents=True, exist_ok=True)
        self.a["scope"] = {"campaign_id": campaign, "campaign_directory": str(cdir) if cdir else None,
                           "variant_id": variant, "variant_directory": str(vdir) if vdir else None}
        self.a["artifacts"] = {"root_directory": str(self.root), "run_id": run_id, "entrypoint": ".agent-artifacts",
                               "run_path": str(self.run.relative_to(self.root)), "run_directory": str(self.run)}
        self.a["startup"] = {"working_directory": str(self.worktree), "assignment_file": str(self.run / "assignment.json"),
                             "bootstrap_file": str(self.run / "worker-start.md"), "protocol_file": str(self.run / "protocol/SKILL.md")}
        self.write_startup()

    def write_startup(self):
        (self.run / "assignment.json").write_text(json.dumps(self.a))
        (self.run / "worker-start.md").write_text(self.render_bootstrap())
        (self.run / "protocol").mkdir(exist_ok=True)
        (self.run / "protocol/SKILL.md").write_text("Frozen protocol")

    def render_bootstrap(self):
        template = (ROOT / "templates/worker-start.md").read_text()
        scope, artifacts, startup = (self.a[k] for k in ("scope", "artifacts", "startup"))
        values = {
            "<assignment-absolute-path>": startup["assignment_file"],
            "<protocol-absolute-path>": startup["protocol_file"],
            "<required-reading-list-with-absolute-paths>": "\n".join(self.a["inputs"]) or "not applicable",
            "<working-directory-absolute-path>": startup["working_directory"],
            "<repository-absolute-path>": self.a["project"]["repository"],
            "<worktree-absolute-path-or-not-applicable>": self.a["project"]["worktree"] or "not applicable",
            "<artifact-root-absolute-path>": artifacts["root_directory"],
            "<campaign-id-and-absolute-directory-or-not-applicable>": f"{scope['campaign_id']}: {scope['campaign_directory']}" if scope["campaign_id"] else "not applicable",
            "<variant-id-and-absolute-directory-or-not-applicable>": f"{scope['variant_id']}: {scope['variant_directory']}" if scope["variant_id"] else "not applicable",
            "<run-id-and-absolute-directory>": f"{artifacts['run_id']}: {artifacts['run_directory']}",
            "<absolute-link-path-to-artifact-root-or-not-applicable>": f"{self.a['project']['worktree']}/.agent-artifacts -> {artifacts['root_directory']}" if artifacts["entrypoint"] else "not applicable",
            "<required-output-list-with-absolute-destinations>": "\n".join(str(self.run / path) for path in self.a["required_outputs"]),
        }
        self.assertEqual(set(values), set(re.findall(r"<[A-Za-z][A-Za-z0-9-]*>", template)))
        for marker, value in values.items():
            template = template.replace(marker, value)
        return template

    def manifest(self, role="test", verdict="passed"):
        self.a["role"] = role
        self.a["git"]["target_commit"] = "b" * 40
        self.a["git"]["branch"] = None
        self.a["permissions"]["modify_source"] = False
        m = json.loads((ROOT / "templates/run-manifest.json").read_text())
        m.update(run_id=self.a["artifacts"]["run_id"], agent={"name": "worker", "role": role}, status="completed")
        m["scope"] = {k: self.a["scope"][k] for k in ("campaign_id", "variant_id")}
        m["git"] = dict(self.a["git"], worktree=str(self.worktree), result_commit=None)
        m["timestamps"] = {k: "2026-09-21T10:00:00Z" for k in m["timestamps"]}
        m["preflight"] = {
            "status": "passed", "assignment_id": self.a["assignment_id"],
            "assignment_file": self.a["startup"]["assignment_file"], "protocol_file": self.a["startup"]["protocol_file"],
            "root_directory": str(self.root), "run_directory": str(self.run),
            "required_output_destinations": [str(self.run / p) for p in self.a["required_outputs"]],
            "working_directory": self.a["startup"]["working_directory"],
            "repository": self.a["project"]["repository"], "worktree": str(self.worktree),
            **self.a["scope"], "run_id": self.a["artifacts"]["run_id"],
            "artifact_link_target": str(self.root), "read_inputs": self.a["inputs"],
        }
        m["result"] = {"verdict": verdict, "evidence": ["tests/raw.json", "report.md"]}
        if role == "test":
            m["result"].update(passed=4, failed=1 if verdict == "failed" else 0, skipped=0)
        if role in {"audit", "review"}:
            m["result"]["blocking_findings"] = 1 if verdict == "invalid" else 0
        m["artifacts"] = ["tests/raw.json", "report.md"]
        (self.run / "tests").mkdir(exist_ok=True)
        (self.run / "tests/raw.json").write_text('{"observations": [1, 2, 3]}')
        (self.run / "report.md").write_text("Evidence report")
        (self.run / "manifest.json").write_text(json.dumps(m))
        self.write_startup()
        return m

    def test_valid_variant_contract_and_files(self):
        self.assertEqual([], validator.validate_assignment(self.a, True))

    def test_all_canonical_scopes(self):
        for campaign, variant in [(None, None), ("campaign", None), ("campaign", "V002")]:
            with self.subTest(campaign=campaign, variant=variant):
                self.place_run(campaign, variant, "run-02")
                self.assertEqual([], validator.validate_assignment(self.a, True))

    def test_rejects_legacy_round_and_schema_version(self):
        self.a["scope"]["round_id"] = "R001"
        self.assertTrue(validator.validate_assignment(self.a))
        del self.a["scope"]["round_id"]
        self.a["schema_version"] = "1.1"
        self.assertTrue(validator.validate_assignment(self.a))

    def test_rejects_old_flat_variant_run_layout(self):
        self.a["artifacts"]["run_directory"] = str(self.root / "campaigns/campaign/runs/implementation-01")
        self.a["artifacts"]["run_path"] = "campaigns/campaign/runs/implementation-01"
        self.assertTrue(validator.validate_assignment(self.a))

    def test_rejects_campaign_link_target(self):
        link = self.worktree / ".agent-artifacts"
        link.unlink()
        link.symlink_to(self.a["scope"]["campaign_directory"])
        self.assertTrue(validator.validate_assignment(self.a, True))

    def test_absolute_fallback_without_link(self):
        (self.worktree / ".agent-artifacts").unlink()
        self.a["artifacts"]["entrypoint"] = None
        self.assertEqual([], validator.validate_assignment(self.a, True))

    def test_artifact_only_aggregation(self):
        self.a["role"] = "aggregation"
        self.a["project"]["worktree"] = None
        self.a["startup"]["working_directory"] = str(self.root)
        self.a["artifacts"]["entrypoint"] = None
        self.a["permissions"]["modify_source"] = False
        self.assertEqual([], validator.validate_assignment(self.a, True))

    def test_implementation_requires_worktree(self):
        self.a["project"]["worktree"] = None
        self.assertTrue(validator.validate_assignment(self.a))

    def test_roles_require_target_and_read_only_permissions(self):
        for role in ("test", "benchmark", "review", "audit"):
            with self.subTest(role=role):
                self.a["role"] = role
                self.assertTrue(validator.validate_assignment(self.a))
                self.a["git"]["target_commit"] = "b" * 40
                self.a["permissions"]["modify_source"] = False
                self.assertEqual([], validator.validate_assignment(self.a))
                self.a["permissions"]["merge"] = True
                self.assertTrue(validator.validate_assignment(self.a))
                self.a["git"]["target_commit"] = None
                self.a["permissions"].update(modify_source=True, merge=False)

    def test_invalid_timestamp_and_moving_commit(self):
        self.a["created_at"] = "not-a-date"
        self.assertTrue(validator.validate_assignment(self.a))
        self.a["created_at"] = "2026-09-21T10:00:00Z"
        self.a["git"]["base_commit"] = "main"
        self.assertTrue(validator.validate_assignment(self.a))

    def test_paths_reject_relative_traversal_and_unowned_output(self):
        for path in ("../outside", "/tmp/report.md", "tests/../../outside", "tests//result.json", "protocol/SKILL.md", "validation.json"):
            with self.subTest(path=path):
                self.a["required_outputs"] = ["manifest.json", "report.md", path]
                self.assertTrue(validator.validate_assignment(self.a))

    def test_variant_needs_campaign(self):
        self.a["scope"].update(campaign_id=None, campaign_directory=None)
        self.assertTrue(validator.validate_assignment(self.a))

    def test_missing_startup_and_input_files(self):
        self.a["inputs"] = [str(self.base / "missing.md")]
        self.assertTrue(validator.validate_assignment(self.a, True))
        self.a["inputs"] = []
        (self.run / "worker-start.md").unlink()
        self.assertTrue(validator.validate_assignment(self.a, True))

    def test_completed_failing_test_is_valid_evidence(self):
        m = self.manifest(verdict="failed")
        self.assertEqual([], validator.validate_manifest(m, self.a, True))
        m["result"]["verdict"] = "passed"
        self.assertTrue(validator.validate_manifest(m, self.a, True))

    def test_no_executed_cases_cannot_pass(self):
        m = self.manifest()
        m["result"]["passed"] = 0
        self.assertTrue(validator.validate_manifest(m, self.a))

    def test_failed_execution_cannot_claim_pass(self):
        m = self.manifest()
        m["status"] = "failed"
        self.assertTrue(validator.validate_manifest(m, self.a))

    def test_missing_output_and_symlink_escape(self):
        m = self.manifest()
        (self.run / "report.md").unlink()
        self.assertTrue(validator.validate_manifest(m, self.a, True))
        outside = self.base / "outside.md"
        outside.write_text("Not archived in run")
        (self.run / "report.md").symlink_to(outside)
        self.assertTrue(validator.validate_manifest(m, self.a, True))

    def test_report_must_be_file_and_directory_evidence_cannot_escape(self):
        m = self.manifest()
        (self.run / "report.md").unlink()
        (self.run / "report.md").mkdir()
        self.assertTrue(validator.validate_manifest(m, self.a, True))
        (self.run / "report.md").rmdir()
        (self.run / "report.md").write_text("report")
        (self.run / "tests/external").symlink_to(self.base)
        m["artifacts"] = ["tests", "report.md"]
        self.assertTrue(validator.validate_manifest(m, self.a, True))

    def test_unrendered_bootstrap_rejected(self):
        (self.run / "worker-start.md").write_text((ROOT / "templates/worker-start.md").read_text())
        self.assertTrue(validator.validate_assignment(self.a, True))

    def test_each_unrendered_directory_placeholder_is_rejected(self):
        template = (ROOT / "templates/worker-start.md").read_text()
        rendered = self.render_bootstrap()
        for marker in set(re.findall(r"<[A-Za-z][A-Za-z0-9-]*>", template)):
            with self.subTest(marker=marker):
                (self.run / "worker-start.md").write_text(rendered + "\n" + marker)
                errors = validator.validate_assignment(self.a, True)
                self.assertTrue(any("unrendered template placeholders" in e and marker in e for e in errors), errors)

    def test_directory_spelling_plural_and_case_are_contract_interfaces(self):
        original = json.dumps(self.a)
        for before, after in [("/campaigns/", "/campaign/"), ("/campaigns/", "/专题/"),
                              ("/variants/", "/variant/"), ("/variants/", "/方案/"),
                              ("/V001/", "/v001/"), ("/V001/", "/V001-double-buffer/"),
                              ("/runs/", "/run/")]:
            with self.subTest(before=before, after=after):
                changed = json.loads(original.replace(before, after))
                self.assertTrue(validator.validate_assignment(changed))

    def test_run_path_is_relative_to_project_root_not_campaign_or_variant(self):
        for wrong in ("runs/implementation-01", "variants/V001/runs/implementation-01"):
            with self.subTest(path=wrong):
                self.a["artifacts"]["run_path"] = wrong
                self.assertTrue(validator.validate_assignment(self.a))

    def test_missing_preflight_mapping_and_wrong_target(self):
        m = self.manifest()
        saved = m["preflight"].pop("run_directory")
        self.assertTrue(validator.validate_manifest(m, self.a))
        m["preflight"]["run_directory"] = saved
        m["git"]["target_commit"] = "c" * 40
        self.assertTrue(validator.validate_manifest(m, self.a))

    def test_invalid_audit_is_valid_handoff_but_not_valid_verdict(self):
        m = self.manifest(role="audit", verdict="invalid")
        self.assertEqual([], validator.validate_manifest(m, self.a, True))
        m["result"]["verdict"] = "valid_with_caveats"
        self.assertTrue(validator.validate_manifest(m, self.a))

    def test_reviewed_manifest_is_pinned_and_commit_matched(self):
        m = self.manifest(role="audit", verdict="valid")
        previous = self.run.parent / "test-01/manifest.json"
        previous.parent.mkdir()
        raw = json.dumps({"run_id": "test-01", "status": "completed", "git": {"target_commit": "b" * 40}}).encode()
        previous.write_bytes(raw)
        self.a["reviewed_runs"] = [{"run_id": "test-01", "manifest_file": str(previous), "manifest_sha256": hashlib.sha256(raw).hexdigest()}]
        m["reviewed_runs"] = [str(previous)]
        self.assertEqual([], validator.validate_assignment(self.a, True))
        self.assertEqual([], validator.validate_manifest(m, self.a, True))
        previous.write_bytes(raw + b"\n")
        self.assertTrue(validator.validate_assignment(self.a, True))
        self.a["reviewed_runs"][0]["manifest_sha256"] = hashlib.sha256(previous.read_bytes()).hexdigest()
        self.a["git"]["target_commit"] = "c" * 40
        self.assertTrue(validator.validate_assignment(self.a, True))

    def test_parallel_variant_destinations_do_not_retarget_link(self):
        old_run = self.run
        (old_run / "logs").mkdir()
        self.place_run("campaign", "V002", "test-02")
        (old_run / "logs/late.log").write_text("late output remains with original producer")
        self.assertFalse((self.run / "logs/late.log").exists())
        self.assertEqual(self.root, (self.worktree / ".agent-artifacts").resolve())
        self.assertEqual([], validator.validate_assignment(self.a, True))

    def test_cli_handoff(self):
        self.manifest()
        self.assertEqual(0, validator.main([str(self.run / "assignment.json"), "--manifest", str(self.run / "manifest.json"), "--check-files"]))

    def test_document_examples_match_schemas(self):
        examples = [json.loads(block) for block in re.findall(r"```json\n(.*?)\n```", (ROOT / "SKILL.md").read_text(), re.S)]
        for data in examples:
            if "assignment_id" in data:
                self.assertEqual([], validator.validate_assignment(data))
            if "assignment_file" in data:
                self.assertEqual([], validator.schema_errors(data, "run-manifest.schema.json"))
                assignment = next(x for x in examples if "assignment_id" in x)
                self.assertEqual([], validator.validate_manifest(data, assignment))


if __name__ == "__main__":
    unittest.main()
