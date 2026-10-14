# Worktree-Based Operator Engineering Protocol

面向华为昇腾算子工程的轻量多 Agent 协作 Skill：隔离代码工作区，持久保存实验产物，支持多 Variant、多次执行与状态追踪。

## 默认工作方式

- 只有 Coordinator 与 Worker 两类职责；实现、测试、benchmark、审查是任务类型。
- 优先复用合适的隔离工作区，不重复管理宿主创建的 worktree。
- 每个 Campaign 一个状态索引，每个 Variant 一份方案说明，每个 Run 两份交接文档。
- 同一 Worker 可完成实现、自测和测量；不为每一步新建角色或执行。
- 所有方案 Run 归属 Variant，不设置额外轮次层级。
- 产物位于 worktree 外，失败和中断证据同样保留，清理工作树不会清理实验历史。
- 仅用于昇腾硬件或 CANN 算子工程，不用于通用软件开发或仅面向其他后端的任务。

## 目录

项目级布局必须如下，主仓库保留实际目录名：

```text
<project-container>/
├── <primary-repository-name>/
├── worktrees/
│   └── <task-worktree>/
└── agent-artifacts/
```

`worktrees/` 和 `agent-artifacts/` 与主仓库平级，禁止放在主仓库内部。
Coordinator 从 Git 元数据识别主仓库，不将当前 linked worktree 或 cwd 当成主仓库。
准备完成前须创建或复用两个平级目录并报告实际绝对路径。权限、路径冲突或宿主限制需先确认例外，
不能默默改变布局；旧的错误目录不自动迁移。

产物根目录内部：

```text
agent-artifacts/
└── campaigns/<campaign>/
    ├── campaign.json
    ├── README.md
    ├── baseline/                   # 按需
    └── variants/V001/
        ├── proposal.md
        └── runs/<run-id>/
            ├── task.md
            ├── result.md
            └── ...                 # 真实测试、日志、性能数据等
```

campaign.json 由 Coordinator 单独更新，记录 Campaign/Variant/Run 状态、关联和决策。
Worker 只写自己的执行产物。Run 完成不表示测试通过或方案已被接受。
同一 Variant 可多次执行，Run 固定归属一个 Variant；新测量不覆盖旧结果。

创建 worktree 后，Coordinator 主动询问是否创建同名 Campaign，等待明确答复。
用户未说明 worktree 用途时，追加询问用途和目标；已有明确说明则不重复问。
确认创建或复用 Campaign 后，将用途写入 `.agent-artifacts/README.md` 的“工作树用途”节，
新专题同时填写 `campaign.json.objective`；复用专题不擅自改写其总目标。
未确认 Campaign 时不为记录用途偷偷创建目录；未授权创建 worktree 时先确认创建意图。
选择是：以工作树实际目录名创建 `agent-artifacts/campaigns/<worktree-name>/`，
初始化 campaign.json 和 README.md，并将 worktree 内的 `.agent-artifacts` 链接到该 Campaign。
选择否或未答复：只保留工作树，不创建 Campaign 或链接，不启动实验。
同名专题已存在时先询问是否复用；链接冲突不覆盖。Variant 与 Run 在实际实验时按需创建。
任务给出绝对产物路径，Git 忽略只配置在仓库本地。
已有实验产物、路径和映射不删除或自动迁移；不再提供旧版合同兼容。

## 安装

从 GitHub 安装：

```bash
npx skills add https://github.com/Hirozy/worktree-based-operator-engineering-protocol
```

从 GitCode 安装：

```bash
npx skills add https://gitcode.com/Hirozy/worktree-based-operator-engineering-protocol.git
```

## 使用

Agent 启动时先用 Git 元数据识别位置：在任务 worktree（包括子目录）默认作为 Worker，
在主仓库或已确认的项目容器默认作为 Coordinator。任务入口缺失时询问，不自动转为编排者。
用户明确要求时，Coordinator 根据 templates/project-context.md 在主仓库上层生成项目 AGENTS.md，
简述主仓库、worktrees、agent-artifacts 的作用；保留已有说明，共享父目录需先确认作用范围。
上层说明仅解释布局，不作为启动依赖；不为注入 Worker 身份修改项目自带的指令文件。

在支持 Agent Skills 的工具中调用：

```text
$worktree-based-operator-engineering-protocol
```

描述目标、昇腾后端、约束及是否需要并行比较。例如：

> 比较这个昇腾算子的两种优化方案。分别在隔离工作树实现，保留正确性和性能证据，
> 同一 NPU 上串行测量，记录比较结论；未经确认不合并或删除工作树。

Coordinator 根据 templates/worker-prompt.md 输出准确启动目录和一段已填充的提示词，
包含 Worker 身份、目标环境可读的 SKILL.md 与 task.md 绝对路径。
用户手动启动 Agent 并粘贴提示；Coordinator 不自动启动 Agent。
尚未分配任务或路径不确定时先补齐信息，不输出含占位符的启动提示，也不假装 Worker 已运行。
不依赖空白会话自动发现 Skill，不再默认创建 worker-start 或复制全量协议。
只请求准备工作区时，返回路径和任务入口，不自动开始执行。

## 按需能力

- references/experiments.md：实验身份、索引、状态、恢复与所有权。
- references/directory-context.md：当前目录识别、角色选择和上层说明的安全生成。
- references/benchmarking.md：正确性与性能证据、环境和设备隔离。
- templates/task.md、result.md、proposal.md、campaign.json：轻量模板。
- templates/worker-prompt.md：Coordinator 输出给用户手动粘贴的启动提示，不复制成每个 Run 的文件。

只保留轻量流程。独立审查仍作为 Worker 任务执行，不引入另一套合同或状态系统。
不依赖 jsonschema、uv、调度框架或状态服务。

## 开发验证

```bash
python3 -m unittest discover -s tests -v
```
