---
name: worktree-based-operator-engineering-protocol
description: "仅用于华为昇腾硬件或 CANN 软件栈的算子开发、优化、移植、重构、验证、基准测试或审计。通过 Coordinator 与 Worker 两类职责、隔离 Git worktree 和持久化 Campaign/Variant/Run 实验记录协调多 Agent。禁止用于普通软件开发、非算子任务或仅面向非昇腾后端的任务。"
---

# 基于 Worktree 的昇腾算子工程

默认采用轻量流程：隔离代码、明确任务、保存证据、更新实验状态。
不要为了符合协议生成空目录、重复报告或尚未发生阶段的占位文件。

## 适用范围

仅处理明确面向昇腾硬件或 CANN 的算子工程，包括新算子开发与已有实现优化。
后端不明确时先确认；不将本 Skill 用作通用 worktree 管理工具。
遵守用户授权和仓库说明；Skill 不授予自动提交、推送、合并或删除权限。

## 两类职责

| 职责 | 工作 |
|---|---|
| Coordinator | 明确目标和依赖，分配 Campaign/Variant/Run 与工作区，派发、核验、维护共享索引、组织集成和清理 |
| Worker | 在授权范围内实现、测试、benchmark、审查或集成，将事实和证据写入自己的 Run |

实现、测试、审计、集成是任务类型，不是额外角色。
Coordinator 同时负责汇总，不为维护文档单独启动 Agent。
简单串行任务可由同一个 Agent 兼任；并行时必须明确当前写入者。
一个 Worker 可在一个 Run 内实现、测试和测量，不按步骤强制拆 Run。
需要独立审计时由另一个 Worker 执行；自测不能标为独立审计。
共享索引由 Coordinator 单写，方案说明也必须指定唯一写入者。

## 核心约束

- 并行修改代码的 Worker 各有独立工作区；从分配的 worktree 根目录执行代码操作。
- Worktree 是代码位置，Run 是执行历史；一个 worktree 可顺序承载多个 Run。
- 持久产物存放在 worktree 外的项目级 `agent-artifacts/`，不能仅存在于聊天中。
- Run 属于具体 Variant；不得将方案 Run 放到 Campaign 下与 variants 同级。
- 不覆盖已结束的执行证据，失败、中断和被拒绝方案也保留。
- 结果绑定准确源码状态；未提交时记录基础 commit 并保存可恢复补丁及必要未跟踪源码。
- 执行完成、验证通过、方案接受是不同结论，不能相互替代。
- 删除工作树前，确认生产进程已停止，代码和必需证据可恢复，且有清理授权。
- 不记录密钥、凭据或未脱敏的敏感环境信息。

## 先选择工作方式

1. 检查已有任务说明、Git 状态、工作区占用及用户约定，不重写已有明确计划。
2. 已有合适的隔离 worktree 就复用；确认属于目标仓库且无其他活跃写入者。
3. 需要创建时优先使用宿主可用的原生能力；已有适用工具可复用，否则使用 Git。
4. 从明确源码起点创建，不猜测默认分支，不要求主目录名为 `repo`。
5. 原生工作区的创建与清理交给其宿主管理，不重复接管或创建嵌套 worktree。
6. 隔离失败时报告阻塞，不退回多人共享的可写 checkout。
7. 单 Agent 简单任务不必另起 Coordinator，但仍保存实验记录。

并行前声明模式：
- 分工：不同子任务，按依赖顺序集成。
- 竞争：同一目标的多个方案，验证比较后选择，不全部合并。
- 验证：检查指定源码状态，不擅自修改被审查实现。

## 持久目录

```text
agent-artifacts/
└── campaigns/<campaign>/
    ├── campaign.json
    ├── README.md
    ├── baseline/                       # 有适用基线时创建
    └── variants/
        └── V001/
            ├── proposal.md
            └── runs/<run-id>/
                ├── task.md
                ├── result.md
                └── ...                 # 真实日志、测试、测量与补丁
```

只创建当前需要的目录。单方案任务使用一个 Campaign、一个 Variant。
沿用已有专题，不因换 Agent 或重开会话重复创建。
Campaign 内 Variant ID 唯一；同一方案持续迭代时保持身份。
每个 Run 固定归属一个 Variant；多次迭代以独立 Run 记录，不增加轮次实体。
独立辅助操作无需伪造方案或 Run；其结论由 Coordinator 记入专题 README。
需要可追溯的测试或测量则归属被验证方案的 Run。

现有链接语义保持：
`<worktree>/.agent-artifacts -> <project-container>/agent-artifacts/`。
不得改指向 Campaign、Variant 或 Run；现有历史链接不自动迁移或重定向。
通过 Git 元数据解析仓库本地 excludes 文件，幂等加入 `/.agent-artifacts` 并验证忽略结果。
不修改全局 Git 配置，不覆盖真实目录或已跟踪入口；冲突时先报告。
无法使用链接时直接传绝对路径。链接只是访问入口，不是权限或任务发现机制。
任务明确给出绝对 Run 路径，并将其传给产出证据的子进程；不通过 cwd 或 latest 推导。

## 任务与启动

每个派发 Run 使用 `templates/task.md`，填入真实值，删去不适用的可选项。
它是唯一任务入口，包含目标、范围、身份、路径、源码起点、必要输入及验收要求。
同一会话的明确计划可以直接引用，不再生成另一份计划或合同。

新 Agent 不继承主 Agent 的上下文。启动提示必须明确：
```text
先读取 <task.md 的绝对路径>，确认工作区、源码起点和产物目录，
遵守其中的任务边界，再开始执行；不一致时停止并报告。
```

自动派发时将上述要求放入初始提示；人工启动时提供准确目录和同样的提示。
若用户要求零提示启动，先确认该 Agent 的项目指令发现规则，再安全加入任务入口。
保留现有说明，不覆盖跟踪文件，不假设所有 Agent 自动读取相同文件。
没有安全自动入口时明确回退到启动提示，不声称空白会话会自动发现任务。
不要生成单独 worker-start、全量协议快照或默认 JSON 合同。
将必要约束写入 task；复杂参考资料只提供本任务需要的路径。
启动前核实仓库、源码、读写路径、必要输入和工作区占用；不生成额外握手报告。

## 执行与交接

1. Coordinator 建立或复用专题，确定当前问题、方案及 Run，登记 pending。
2. 创建 task 与工作区；仅请求准备环境时报告路径并停止，不启动实验。
3. Worker 核实后由 Coordinator 登记 running，开始授权任务。
4. 测试与测量尽量直接输出到外部 Run；临时文件可留工作区，但交接前收集必需证据。
5. Worker 在 result 中记录源码状态、命令、结论、证据路径、失败及未执行项。
6. Coordinator 核对实际证据后更新索引；不足时记录原因，不宣称通过。
7. 有授权时集成选定结果，针对集成后的源码重新验证，再按条件清理。

活跃 Run 中的调试和补充不强制拆分；已结束后的重试、新测量或独立审查新建 Run。
结束后的 task/result/证据保留，后续纠错由新 Run 引用旧 Run，不重写旧结论。
任务范围实质变化时停止旧执行并重新派发；不暗改正在执行的任务。
Worker 崩溃时保留部分证据，Coordinator 在索引记录中断；不冒充 Worker 补写结果。

## 实验状态

`campaign.json` 是共享状态的唯一索引；result 是执行事实，不是另一份状态数据库。
Coordinator 在派发、开始、结束和决策时更新，不要求逐命令记录。
使用 `templates/campaign.json` 的结构，按需填充，禁止创建示例中的虚构执行。
Campaign、Variant、Run 的关联与状态规则见 [实验管理](references/experiments.md)。
并行工作前确认单一 Coordinator；交接期间停止旧写入者，再校对索引接管。

## 按需参考

| 需要 | 读取 |
|---|---|
| 新建或恢复实验、方案比较、维护状态 | [experiments.md](references/experiments.md) |
| 正确性验证、baseline、benchmark、profiling | [benchmarking.md](references/benchmarking.md) |
| 用户明确要求旧版结构化合同与严格验收 | [strict-audit.md](references/strict-audit.md) |

普通任务不自动升级严格模式；独立审查本身也不要求全套旧协议。
references 是按问题读取的知识，不是每个 Worker 的必读清单。
历史执行沿用保留的协议、路径和证据，不用新版模板解释或迁移旧合同。
