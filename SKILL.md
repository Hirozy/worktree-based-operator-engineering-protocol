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

## 启动时识别位置与角色

先按 [目录识别](references/directory-context.md) 用 Git 元数据识别当前位置，再选择职责。
在已注册的任务 worktree 根目录或其子目录中，自动作为 Worker；切到该工作树根目录执行。
不因缺少任务文件或 Campaign 就转为 Coordinator，不自行创建另一个 worktree 或重建实验。
在已确认的项目容器或主仓库中默认作为 Coordinator；位置未知或有歧义时先询问，不修改文件。
用户明确指定的职责优先，但不会自动授予共享文件、其他工作区或 Git 操作的权限。
上层目录说明仅在用户要求时按 `templates/project-context.md` 提供，不作为 Worker 启动依赖。
禁止为了 Worker 启动创建或修改项目的 `AGENTS.md`、`CLAUDE.md` 等原生指令文件。
Coordinator 输出启动提示，由用户手动注入；目录角色识别在读取本 Skill 后生效，不保证空白会话自动加载。

## 两类职责

| 职责 | 工作 |
|---|---|
| Coordinator | 明确目标和依赖，分配 Campaign/Variant/Run 与工作区，派发、核验、维护共享索引、组织集成和清理 |
| Worker | 在授权范围内实现、测试、benchmark、审查或集成，将事实和证据写入自己的 Run |

实现、测试、审计、集成是任务类型，不是额外角色。
Coordinator 同时负责汇总，不为维护文档单独启动 Agent。
简单串行任务可由明确承担编排职责的 Agent 兼任；任务 worktree 内默认只作为 Worker。
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
3. 需要创建时，仅使用能满足下方平级布局的原生能力或已有工具，否则使用 Git。
4. 从明确源码起点创建，不猜测默认分支，不要求主目录名为 `repo`。
5. 原生工作区由宿主管理；若位置不符合平级布局，先报告并请求明确例外，不默认为合规或重复创建。
6. 隔离失败时报告阻塞，不退回多人共享的可写 checkout。
7. 单 Agent 简单任务不必另起 Coordinator，但仍保存实验记录。

并行前声明模式：
- 分工：不同子任务，按依赖顺序集成。
- 竞争：同一目标的多个方案，验证比较后选择，不全部合并。
- 验证：检查指定源码状态，不擅自修改被审查实现。

## 项目级布局（创建前必须确认）

```text
<project-container>/
├── <primary-repository-name>/    # Git 主仓库，保留实际名称
├── worktrees/                    # 本项目的任务工作树
│   └── <task-worktree>/
└── agent-artifacts/              # 持久产物根目录
```

主仓库、`worktrees/`、`agent-artifacts/` 必须是同一父目录下的三个不同目录。
禁止在主仓库内部创建后两者，也禁止将主仓库本身当成 project-container。
Coordinator 在分配实验产物或创建工作树前执行以下检查：

1. 对已知 checkout 执行 `git worktree list --porcelain`，结合 `git rev-parse --git-common-dir`
   识别实际主工作树；`git rev-parse --show-toplevel` 只表示当前 checkout，不一定是主仓库。
   从 linked worktree 启动时仍以主仓库定位父目录，不以当前 cwd 的父目录定位。
2. 解析真实路径：`project_container = parent(primary_repository)`；
   `worktrees_root = project_container/worktrees`；
   `artifact_root = project_container/agent-artifacts`。不硬编码主仓库名为 repo。
3. 检查父目录写权限、已有目录/符号链接及其他项目占用。确认安全后复用或创建两个平级目录，
   包括复用既有工作树时保留 `worktrees/` 入口；这是项目基础布局，不是预建空实验骨架。
4. 新任务工作树放在 `worktrees_root/<task-worktree>`，从明确 commit 创建；
   创建后检查真实路径仍符合该位置，artifact_root 不位于任何代码工作树内。
5. 返回实际主仓库、project_container、worktrees_root、artifact_root、任务工作树的绝对路径，
   核实两个根目录存在且与主仓库平级，再报告准备完成。

权限不足、裸仓库、多仓库共用父目录、同名路径冲突或宿主固定位置无法满足布局时，
报告冲突并取得用户明确布局选择；禁止静默退回主仓库内创建。
发现旧产物放错位置时不自动移动、删除或重定向链接，先给出迁移方案并确认没有活跃写入者。

## 创建后确认 Campaign

每次新建 worktree 成功后，主动询问：“是否为此 worktree 创建同名 Campaign，并链接到其 .agent-artifacts？”
等待用户明确答复；不能将创建 worktree 的授权视为创建 Campaign 的授权。
如果用户没有说明该 worktree 的用途，追加询问：“这个 worktree 用来做什么？希望完成什么目标？”
可与 Campaign 确认一起询问；已有明确用途时不重复问，也不从目录名推测用途。
创建 worktree 本身仍须获得授权；用户未表达创建意图时，先确认是否需要创建，不能先创建再补问。
- 选择是：以实际工作树目录的 basename 为 campaign_id（不是分支名），在
  `artifact_root/campaigns/<worktree-name>/` 创建 Campaign，填充 campaign.json 与 README.md。
  仅写已知目标和身份，未知目标标为待确认；不预建 Variant、Run 或虚构结果。
  将 `<worktree>/.agent-artifacts` 链接到该 Campaign，验证解析后的真实目标及本地忽略规则。
  收到用途答复后，在 `.agent-artifacts/README.md` 的“工作树用途”节记录实际工作树名称、
  绝对路径、用户说明的用途和目标；新 Campaign 的 `campaign.json.objective` 同步记录目标。
  复用 Campaign 时只补充对应工作树的用途，不擅自改写专题总目标或覆盖其他工作树记录。
  用途未答复时标为待确认并保留问题，不猜测目标、不启动实验。
- 选择否或尚未答复：只保留已创建的工作树，不创建 Campaign、链接、Variant 或 Run，不启动实验。
  已收到的用途可在回复中保留，明确尚未落盘；不能为了写用途而暗中创建 Campaign 或实体 .agent-artifacts 目录。
- 同名 Campaign 已存在：说明冲突，询问是否复用；确认身份与所有权后才链接，禁止覆盖已有内容。
- 链接已存在且目标一致时复用；目标不同或入口为真实目录/文件时，报告冲突，不覆盖或重定向。
  历史映射调整须另行授权且确认旧 Worker 与产物生成进程已停止。

只请求创建时，此确认及可选 Campaign 初始化就是交付终点；不自动派发 Worker。
复用已有工作树时沿用明确分配的 Campaign，不重复创建；未分配时先确认，再开始实验。

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

用户确认 Campaign 后，只创建当前需要的目录。开始单方案实验时使用一个 Campaign、一个 Variant。
沿用已有专题，不因换 Agent 或重开会话重复创建。
Campaign 内 Variant ID 唯一；同一方案持续迭代时保持身份。
每个 Run 固定归属一个 Variant；多次迭代以独立 Run 记录，不增加轮次实体。
独立辅助操作无需伪造方案或 Run；其结论由 Coordinator 记入专题 README。
需要可追溯的测试或测量则归属被验证方案的 Run。

新建 Campaign 的链接语义：
`<worktree>/.agent-artifacts -> <project-container>/agent-artifacts/campaigns/<worktree-name>/`。
入口指向 Campaign 根目录，不是项目产物根目录、Variant 或 Run；历史链接不自动迁移或重定向。
例如任务文件通过 `.agent-artifacts/variants/V001/runs/<run-id>/task.md` 访问。
通过 Git 元数据解析仓库本地 excludes 文件，幂等加入 `/.agent-artifacts` 并验证忽略结果。
不修改全局 Git 配置，不覆盖真实目录或已跟踪入口；冲突时先报告。
无法使用链接时直接传绝对路径。链接只是访问入口，不是权限或任务发现机制。
任务明确给出绝对 Run 路径，并将其传给产出证据的子进程；不通过 cwd 或 latest 推导。

## 任务与启动

每个派发 Run 使用 `templates/task.md`，填入真实值，删去不适用的可选项。
它是唯一任务入口，包含目标、范围、身份、路径、源码起点、必要输入及验收要求。
同一会话的明确计划可以直接引用，不再生成另一份计划或合同。

新 Agent 不继承主 Agent 的上下文。采用手动注入：Coordinator 输出准确的启动目录，
并按 `templates/worker-prompt.md` 渲染一段可直接复制的提示词，由用户启动 Agent 后粘贴。
提示中明确 Worker 身份、项目原有说明、SKILL.md 与 task.md 的绝对路径和执行边界。
验证 Skill 路径是目标 Worker 环境中可访问的实际路径，不照搬 Coordinator 本机路径。
任务尚未分配或路径无法确认时先报告缺项，不输出含占位符的“可执行提示”，不为此伪造 Run。
输出提示不代表 Worker 已启动；Run 保持 pending，收到实际启动确认后才更新 running。
不自动启动 Agent，不修改项目原生指令或全局配置，不依赖环境变量、上层说明或空白会话自动加载。
不要生成单独 worker-start、全量协议快照或默认 JSON 合同。
将必要约束写入 task；复杂参考资料只提供本任务需要的路径。
启动前核实仓库、源码、读写路径、必要输入和工作区占用；不生成额外握手报告。

## 执行与交接

1. Coordinator 确认项目级平级布局，创建或复用工作区；新建后完成 Campaign 询问与可选初始化。
2. 仅请求准备环境时报告路径并停止；获准执行且 Campaign 已确认后，确定方案及 Run、登记 pending 并创建 task。
3. Coordinator 给出启动目录与提示词，用户手动注入；Worker 核实后由 Coordinator 登记 running，开始授权任务。
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

独立审查作为 Worker 任务执行，仍使用 task.md、result.md 和原始证据。
references 是按问题读取的知识，不是每个 Worker 的必读清单。
不再提供旧版合同或校验兼容；已有实验产物不删除或自动迁移，格式不匹配时报告并请求处理方案。
