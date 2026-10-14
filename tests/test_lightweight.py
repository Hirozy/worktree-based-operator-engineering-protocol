import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class LightweightTests(unittest.TestCase):
    def test_campaign_starts_without_fabricated_records(self):
        campaign = json.loads((ROOT / "templates/campaign.json").read_text())
        self.assertEqual(campaign["schema_version"], "lightweight-1")
        self.assertEqual(campaign["status"], "active")
        for field in ("decisions", "variants", "runs"):
            self.assertEqual(campaign[field], [])

    def test_entrypoint_is_short_and_references_resolve(self):
        skill = (ROOT / "SKILL.md").read_text()
        self.assertLessEqual(len(skill.splitlines()), 200)
        documents = [ROOT / "SKILL.md", *ROOT.glob("references/*.md")]
        for document in documents:
            if document.name == "legacy-v2.md":
                continue
            for target in re.findall(r"\]\(([^)]+)\)", document.read_text()):
                with self.subTest(document=document.name, target=target):
                    self.assertTrue((document.parent / target).is_file())

    def test_worker_templates_include_handoff_and_provenance(self):
        task = (ROOT / "templates/task.md").read_text()
        result = (ROOT / "templates/result.md").read_text()
        for field in ("Campaign", "Variant", "Run", "基础 commit", "产物目录", "验收"):
            self.assertIn(field, task)
        for field in ("commit", "未提交", "证据", "进程"):
            self.assertIn(field, result)

    def test_sibling_layout_is_explicit(self):
        skill = (ROOT / "SKILL.md").read_text()
        self.assertIn("project_container = parent(primary_repository)", skill)
        self.assertIn("worktrees_root = project_container/worktrees", skill)
        self.assertIn("artifact_root = project_container/agent-artifacts", skill)
        self.assertIn("git worktree list --porcelain", skill)
        self.assertIn("禁止在主仓库内部创建后两者", skill)
        self.assertIn("两个根目录存在且与主仓库平级", skill)
        self.assertIn("禁止静默退回主仓库内创建", skill)
        task = (ROOT / "templates/task.md").read_text()
        for field in ("主仓库", "项目容器", "工作树根目录", "产物根目录"):
            self.assertIn(field, task)

    def test_default_does_not_load_legacy_protocol(self):
        skill = (ROOT / "SKILL.md").read_text()
        self.assertNotIn("legacy-v2.md", skill)
        self.assertIn("普通任务不自动升级严格模式", skill)
        self.assertIn("一个 Run 内实现、测试和测量", skill)
        self.assertIn("Run 属于具体 Variant", skill)
        self.assertNotIn("Round", skill)
        self.assertNotIn("rounds", json.loads((ROOT / "templates/campaign.json").read_text()))
        for name in ("references/experiments.md", "templates/task.md", "README.md"):
            text = (ROOT / name).read_text()
            self.assertNotRegex(text, r"(?i)\bround(?:s|_id)?\b")


if __name__ == "__main__":
    unittest.main()
