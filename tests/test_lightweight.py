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
        self.assertLessEqual(len(skill.splitlines()), 220)
        documents = [ROOT / "SKILL.md", *ROOT.glob("references/*.md")]
        for document in documents:
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

    def test_campaign_creation_requires_confirmation(self):
        skill = (ROOT / "SKILL.md").read_text()
        self.assertIn("每次新建 worktree 成功后，主动询问", skill)
        self.assertIn("等待用户明确答复", skill)
        self.assertIn("basename 为 campaign_id（不是分支名）", skill)
        self.assertIn("选择否或尚未答复", skill)
        self.assertIn("同名 Campaign 已存在", skill)
        self.assertIn("<project-container>/agent-artifacts/campaigns/<worktree-name>/", skill)
        self.assertNotIn("不得改指向 Campaign", skill)
        self.assertIn("不预建 Variant、Run", skill)

    def test_worktree_purpose_is_asked_and_persisted(self):
        skill = (ROOT / "SKILL.md").read_text()
        for requirement in (
            "如果用户没有说明该 worktree 的用途，追加询问",
            "已有明确用途时不重复问",
            "先确认是否需要创建",
            "`.agent-artifacts/README.md` 的“工作树用途”节",
            "`campaign.json.objective`",
            "不擅自改写专题总目标",
            "明确尚未落盘",
        ):
            self.assertIn(requirement, skill)

    def test_directory_context_selects_worker_without_dispatch(self):
        skill = (ROOT / "SKILL.md").read_text()
        context = (ROOT / "references/directory-context.md").read_text()
        template = (ROOT / "templates/project-context.md").read_text()
        self.assertIn("自动作为 Worker", skill)
        self.assertIn("git worktree list --porcelain", context)
        self.assertIn("--show-superproject-working-tree", context)
        self.assertIn("没有明确任务入口时询问", context)
        self.assertIn("不自动创建 Campaign", context)
        self.assertIn("共享 Projects 目录", context)
        self.assertIn("不适用于同一父目录下的其他项目", template)
        self.assertIn("包括子目录", template)

    def test_worker_start_uses_manual_prompt(self):
        skill = (ROOT / "SKILL.md").read_text()
        prompt = (ROOT / "templates/worker-prompt.md").read_text()
        self.assertIn("由用户启动 Agent 后粘贴", skill)
        self.assertIn("Run 保持 pending", skill)
        self.assertIn("不自动启动 Agent", skill)
        self.assertIn("禁止为了 Worker 启动创建或修改项目的", skill)
        self.assertIn("你是本次昇腾算子任务的 Worker。", prompt)
        self.assertNotIn("不是 Coordinator", prompt)
        self.assertLessEqual(len(prompt.splitlines()), 10)
        self.assertIn("<worker-accessible-skill-md-absolute-path>", prompt)
        self.assertIn("<task-md-absolute-path>", prompt)
        self.assertIn("项目原有说明", prompt)

    def test_only_lightweight_protocol_is_shipped(self):
        skill = (ROOT / "SKILL.md").read_text()
        self.assertNotIn("legacy-v2.md", skill)
        for name in (
            "references/legacy-v2.md", "references/strict-audit.md",
            "templates/assignment.json", "templates/run-manifest.json",
            "templates/validation.json", "templates/worker-start.md",
            "schemas/assignment.schema.json", "schemas/run-manifest.schema.json",
            "scripts/validate_contract.py", "tests/test_contract.py",
        ):
            self.assertFalse((ROOT / name).exists(), name)
        self.assertIn("一个 Run 内实现、测试和测量", skill)
        self.assertIn("Run 属于具体 Variant", skill)
        self.assertNotIn("Round", skill)
        self.assertNotIn("rounds", json.loads((ROOT / "templates/campaign.json").read_text()))
        for name in ("references/experiments.md", "templates/task.md", "README.md"):
            text = (ROOT / name).read_text()
            self.assertNotRegex(text, r"(?i)\bround(?:s|_id)?\b")


if __name__ == "__main__":
    unittest.main()
