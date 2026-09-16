# Worktree-Based Operator Engineering Protocol

一个面向华为昇腾算子工程的可复用 Skill，通过统一的 Git worktree 协作协议，协调 Codex、Claude Code、Pi、Herdr 等编程 Agent。

## 功能

- 仅适用于明确面向华为昇腾硬件或 CANN 软件栈的算子开发、优化、移植、验证、基准测试和审计任务。
- 为每个修改昇腾算子代码的 Agent 分配独立的 Git worktree，避免并行开发时发生工作区冲突。
- 定义编排者（Coordinator）角色，统一管理 worktree、执行记录（Run）、权限及生命周期状态转换。
- 根据 Git 元数据和现有布局自动识别主仓库的实际目录，不要求目录名为 `repo`，也不重命名现有工作区。
- 使用不可变的任务合同 `assignment.json`，向执行者（Worker）传递准确的路径、提交、输入、输出和产物位置。
- 要求 Worker 执行启动前检查，并由 Coordinator 通过 `validation.json` 记录任务完成验收。
- 将每个专题 worktree 的 `.agent-artifacts` 入口映射到专题（Campaign）根目录，同时将执行产物限制在分配的 Run 目录内。
- 由 Coordinator 直接维护仓库本地的 `.agent-artifacts` Git 忽略规则，不修改全局 Git 配置。
- 要求 Agent 在各自分配的 worktree 根目录启动。
- 将 `manifest.json`、`report.md`、测试、日志、基准测试数据、性能分析数据和补丁保存在临时 worktree 之外的共享 `agent-artifacts/` 区域。
- 将 Worktree 与 Run 分离建模，确保临时工作区删除后，执行历史仍可追溯。
- 使用 `Project > Campaign > Round > Variant > Run > Artifact`（项目 > 专题 > 轮次 > 方案 > 执行 > 产物）逻辑层级组织昇腾算子开发、优化、移植、重构和验证工作。
- 统一规范规格说明、正确性判定依据、验收标准、假设、提案、计划、实现、结果、审计、决策和最终报告。

## 产物目录

默认顶层目录为 `campaigns/` 和独立任务的 `runs/`，均按需创建：

```text
agent-artifacts/
├── campaigns/
│   └── <campaign-id>/
│       ├── README.md
│       ├── manifest.json
│       ├── reference/          # 规格、正确性依据与验收标准
│       ├── baseline/           # 有适用基线时创建
│       ├── variants/
│       │   └── V001/           # 假设、提案、计划、实现、结果、审计、决策
│       ├── runs/
│       │   └── <run-id>/       # 合同、启动引导、协议快照、报告与原始证据
│       └── summary/            # 状态、时间线、对比、决策与最终报告
└── runs/                       # 不属于 Campaign 的执行记录
```

Round 作为元数据保存在专题清单和任务合同中，不再创建轮次目录。Variant 编号在整个 Campaign 内唯一，不随 Round 重置。专题任务的 `.agent-artifacts` 仍指向 Campaign 根目录，合同位于 `.agent-artifacts/runs/<run-id>/assignment.json`；非专题任务的入口指向项目产物根目录。已有历史记录保留原路径，不自动迁移。

## 安装

从 GitHub 安装：

```bash
npx skills add https://github.com/Hirozy/worktree-based-operator-engineering-protocol
```

从 GitCode 安装：

```bash
npx skills add https://gitcode.com/Hirozy/worktree-based-operator-engineering-protocol.git
```

## 使用方法

在支持 Agent Skills 的工具中调用此 Skill：

```text
$worktree-based-operator-engineering-protocol
```

然后描述需要完成的昇腾算子实现、优化、移植、验证、基准测试或审计任务。通用软件开发任务，或仅面向非昇腾后端的算子任务，不应调用此 Skill。

### 新 Agent 的启动引导

新建 worktree 不会继承主 Agent 已加载的 Skill。Coordinator 必须在执行 Run 中保存协议快照 `protocol/`，并根据模板生成 `worker-start.md`，明确指定协议和任务合同的位置。

在分配的 worktree 根目录启动新 Agent 后，发送以下首条指令（将 `<run-path>` 替换为实际路径）：

```text
先读取 .agent-artifacts/<run-path>/worker-start.md，按照其中的指令加载协议和 assignment.json，完成启动前检查后再执行任务。
```

自动启动时，由 Coordinator 将同样的指令作为初始提示传入。不要依赖空白会话自动发现 Skill；不同 Agent 的原生发现机制需单独确认。

## 文件说明

- `SKILL.md`：完整的协作协议与执行指令。
- `templates/assignment.json`：可复用的 Worker 任务合同模板。
- `templates/worker-start.md`：新 Agent 的协议加载与任务启动引导模板。
- `templates/validation.json`：可复用的 Coordinator 完成验收记录模板。
- `schemas/assignment.schema.json`：用于机器校验任务合同的 JSON Schema。
- `README.md`：功能概览与安装说明。
