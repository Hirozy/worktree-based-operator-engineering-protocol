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
- 使用 `Project > Campaign > Round > Variant > Run > Artifact`（项目 > 专题 > 轮次 > 方案 > 执行 > 产物）层级组织昇腾算子开发、优化、移植、重构和验证工作。
- 统一规范规格说明、正确性判定依据、验收标准、假设、提案、计划、实现、结果、审计、决策和最终报告。

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

## 文件说明

- `SKILL.md`：完整的协作协议与执行指令。
- `templates/assignment.json`：可复用的 Worker 任务合同模板。
- `templates/validation.json`：可复用的 Coordinator 完成验收记录模板。
- `schemas/assignment.schema.json`：用于机器校验任务合同的 JSON Schema。
- `README.md`：功能概览与安装说明。
