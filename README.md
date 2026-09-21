# Worktree-Based Operator Engineering Protocol

一个面向华为昇腾算子工程的可复用 Skill，通过统一的 Git worktree 协作协议，协调 Codex、Claude Code、Pi、Herdr 等编程 Agent。

## 功能

- 仅适用于明确面向华为昇腾硬件或 CANN 软件栈的算子开发、优化、移植、验证、基准测试和审计任务。
- 为每个修改昇腾算子代码的 Agent 分配独立的 Git worktree，避免并行开发时发生工作区冲突。
- 定义编排者（Coordinator）角色，统一管理 worktree、执行记录（Run）、权限及生命周期状态转换。
- 根据 Git 元数据和现有布局自动识别主仓库的实际目录，不要求目录名为 `repo`，也不重命名现有工作区。
- 使用不可变的任务合同 `assignment.json`，向执行者（Worker）传递准确的路径、提交、输入、输出和产物位置。
- 要求 Worker 执行启动前检查，并由 Coordinator 通过 `validation.json` 记录任务完成验收。
- 将所有 worktree 的 `.agent-artifacts` 固定映射到项目产物根目录；合约单独绑定绝对 Run 路径，任务切换不改变链接目标。
- 由 Coordinator 直接维护仓库本地的 `.agent-artifacts` Git 忽略规则，不修改全局 Git 配置。
- 要求 Agent 在各自分配的 worktree 根目录启动。
- 将 `manifest.json`、`report.md`、测试、日志、基准测试数据、性能分析数据和补丁保存在临时 worktree 之外的共享 `agent-artifacts/` 区域。
- 将 Worktree 与 Run 分离建模，确保临时工作区删除后，执行历史仍可追溯。
- 使用 `Project > Campaign > Variant > Run > Artifact`（项目 > 专题 > 方案 > 执行 > 产物）层级组织昇腾算子开发、优化、移植、重构和验证工作。
- 统一规范规格说明、正确性判定依据、验收标准、假设、提案、计划、实现、结果、审计、决策和最终报告。

## 产物目录

默认顶层目录为 `campaigns/` 和独立任务的 `runs/`，均按需创建：

```text
agent-artifacts/                         # fixed target for every .agent-artifacts link
├── campaigns/
│   └── <campaign-id>/
│       ├── README.md                    # goal and directory index
│       ├── manifest.json
│       ├── reference/
│       ├── baseline/                    # create when applicable
│       ├── variants/
│       │   └── V001/
│       │       ├── manifest.json        # parent_variant, comparison_variants, commit
│       │       ├── plan.md
│       │       ├── result.md            # conclusions from test/benchmark Runs
│       │       ├── audit.md             # conclusions from independent audit Runs
│       │       ├── decision.md
│       │       └── runs/
│       │           ├── <implementation-run-id>/
│       │           ├── <test-run-id>/
│       │           └── <audit-run-id>/
│       ├── runs/                        # campaign-wide tasks without a Variant
│       └── summary/
└── runs/                                # standalone tasks outside a Campaign
```

v2 移除 Round 的目录、字段和状态。V 表示一个具体方案/假设，在 Campaign 内唯一编号、不重置、不复用；Run 表示一次执行，重测、复审和重试都创建新 Run。方案演进由 `parent_variant` 和精确 `base_commit` 表示，对比对象由 `comparison_variants` 表示。

Worker 可读取完整 Campaign 的上下文，启动时必读文件列入合约 `inputs`。持久产物写入合约给定的绝对 `run_directory`，并将该路径显式传给子进程。Worker 仍可自由使用 shell、编译器、profiler 和临时脚本；交接前须归档支持结论的证据。

测试和审计使用独立的 Run，绑定精确 `target_commit`。审计合约还记录被审查 Run 的 manifest 路径和摘要。`completed` 仅表示执行结束，不能代替测试通过、审计有效或方案被接受。Coordinator 检查真实文件后记录 `validation.json`；缺少证据时不能合并或清理。

已有历史记录保留原路径和协议，不自动迁移。切换旧 worktree 前必须结束旧 Worker 及子进程；仍有任务运行时使用新 worktree，不能重定向旧链接。版本 2.0 的合约和校验器不用于直接解释旧版合同。

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

按合约指定的目录启动 Agent，并发送以下首条指令（替换为具体绝对路径）：

```text
首先读取 <assignment.json 的绝对路径>，再读取 <worker-start.md 的绝对路径>。
在执行任务命令或修改文件前，阅读协议和必读输入，核实目录与链接结构，
回报 assignment、Campaign、Variant、Run 身份及全部产物的准确目标路径。
完成启动前检查后再执行任务；有不一致时报告，不猜测替代路径。
```

自动启动时，由 Coordinator 将同样的指令作为初始提示传入。不要依赖空白会话自动发现 Skill；不同 Agent 的原生发现机制需单独确认。

## 校验

模板含占位符，必须先填写实际路径、完整 commit、身份及验收要求。以下命令中的 `<protocol>` 为本仓库或 Run 内冻结的协议快照路径：

```bash
# 合约结构与路径关系
uv run --no-project --with 'jsonschema[format]==4.26.0' python <protocol>/scripts/validate_contract.py <assignment.json>
# 派发前检查已有目录、链接、输入和启动文件
uv run --no-project --with 'jsonschema[format]==4.26.0' python <protocol>/scripts/validate_contract.py <assignment.json> --check-files
# 提交后检查必需产物、证据路径、身份及 commit 一致性
uv run --no-project --with 'jsonschema[format]==4.26.0' python <protocol>/scripts/validate_contract.py <assignment.json> --manifest <manifest.json> --check-files
# 在本仓库运行回归测试
uv run --no-project --with 'jsonschema[format]==4.26.0' python -m unittest discover -s tests -v
```

校验器只读文件，不限制 Worker 的执行工具，也不自动接管编排。它检查结构、路径、输入摘要和合约/manifest 一致性；实际 Git 状态、进程终止、精度、性能方法和审计结论仍由 Coordinator 与独立审查负责。将校验放入交接流程，才能阻止不合格结果进入合并和清理。

## 文件说明

- `SKILL.md`：完整协作协议与执行指令。
- `templates/assignment.json`：v2 Worker 任务合同。
- `templates/worker-start.md`：合约优先读取、目录结构、身份和产物定位引导。
- `templates/run-manifest.json`：执行状态与结果记录模板。
- `templates/validation.json`：Coordinator 完成验收记录，默认待检查。
- `schemas/assignment.schema.json`：合同结构与角色约束。
- `schemas/run-manifest.schema.json`：Run 身份、执行状态和角色结果结构。
- `scripts/validate_contract.py`：只读合约与交接校验器。
- `tests/test_contract.py`：路径隔离、角色结果、历史输入和异常情况测试。
