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

保留现行映射：worktree 内的 `.agent-artifacts` 指向项目 `agent-artifacts/` 根目录，
不是专题或 Run。任务给出绝对产物路径，Git 忽略只配置在仓库本地。
已有历史合同、路径和映射不自动迁移。

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

在支持 Agent Skills 的工具中调用：

```text
$worktree-based-operator-engineering-protocol
```

描述目标、昇腾后端、约束及是否需要并行比较。例如：

> 比较这个昇腾算子的两种优化方案。分别在隔离工作树实现，保留正确性和性能证据，
> 同一 NPU 上串行测量，记录比较结论；未经确认不合并或删除工作树。

新 Worker 的初始提示必须明确读取 task.md 的绝对路径。
不依赖空白会话自动发现 Skill，不再默认创建 worker-start 或复制全量协议。
只请求准备工作区时，返回路径和任务入口，不自动开始执行。

## 按需能力与兼容

- references/experiments.md：实验身份、索引、状态、恢复与所有权。
- references/benchmarking.md：正确性与性能证据、环境和设备隔离。
- references/strict-audit.md：显式启用旧版严格合同与验收。
- references/legacy-v2.md：保留的旧协议，普通 Worker 不加载。
- templates/task.md、result.md、proposal.md、campaign.json：轻量模板。

旧 JSON 合同模板、schema、校验脚本和测试保留为严格模式及历史兼容用途。
它们不适用于 lightweight-1 索引，普通任务不需要安装校验依赖。
独立审查不自动触发严格模式。现阶段没有新增调度框架、状态服务或工具依赖。

## 开发验证

```bash
python3 -m unittest discover -s tests -p 'test_lightweight.py' -v
uv run --no-project --with 'jsonschema[format]==4.26.0' python -m unittest discover -s tests -v
```
