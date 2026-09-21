---
name: worktree-based-operator-engineering-protocol
description: "仅用于面向华为昇腾硬件或 CANN 软件栈的算子工程，通过编排者角色、不可变任务合约、独立 Git worktree 和持久化外部产物，协调 Codex、Claude、Pi、Herdr 等编程 Agent。仅在任务明确涉及昇腾算子开发、优化、移植、重构、验证、基准测试或审计时使用。禁止用于通用多 Agent 软件开发、非算子任务，或仅面向 CUDA、ROCm、CPU 等非昇腾后端的算子任务。"
---

# 基于 Git worktree 的昇腾算子工程协议

本协议用于隔离并发代码修改，在删除工作树后保留执行证据，并将昇腾算子迭代过程组织为可复现的决策记录。

一个专题（Campaign）可以开发新算子、优化现有昇腾实现、将其他后端的算子移植到昇腾、在保持行为的前提下重构，或验证已有实现。禁止假定每个专题开始时都已有经过优化、甚至能够运行的实现。

协议不限定 Agent 工具，但限定目标平台。Codex、Claude Code、Pi、Herdr、人工开发者、CI 执行器、基准测试执行者、审查者和集成者均可参与符合适用范围的昇腾算子任务。

## 适用范围

只有任务明确面向华为昇腾算子工程时，才使用本 Skill。适用任务包括：

- 使用 Ascend C、TBE、TIK、CANN 自定义算子 API 或其他面向昇腾的工具链开发算子。
- 将自定义算子接入 CANN、`torch_npu`、昇腾上的 MindSpore，或其他明确面向昇腾的框架与运行时。
- 在昇腾硬件上进行算子优化、性能分析、基准测试、验证、代码审查或审计。
- 将 CUDA、ROCm、CPU 等后端的算子移植到明确指定的昇腾目标。

禁止将本 Skill 用于通用 Git worktree 管理、普通多 Agent 软件开发、应用代码、不涉及算子实现的模型级优化，以及仅面向非昇腾后端的算子任务。硬件或后端目标未指定时，禁止自动选用本 Skill。

## 术语与约束用语

正文统一使用中文；字段名、路径、命令、状态值及机器接口保留英文。主要术语如下，后文按角色和上下文使用中文简称：

| 术语 | 含义 |
|---|---|
| 编排者（Coordinator） | 负责派发、协调、验收和流程推进 |
| 执行者（Worker） | 根据合约执行具体任务 |
| 专题（Campaign） | 一个完整的算子工程目标 |
| 方案（Variant，简称 V） | 一个具体假设或实现方案 |
| 执行记录（Run） | 一次执行及其身份、状态和证据；后文简称“执行” |
| 工作树（Git worktree） | 独立的代码检出与操作位置 |
| 产物（Artifact） | 执行产生的原始或派生证据 |
| 汇总者（Aggregator） | 共享汇总文件的唯一写入者 |
| 集成者（Integrator） | 负责合并和集成验证 |
| 正确性判定依据（Oracle） | 用于判断实现结果是否正确的参考依据 |

“必须”表示完成协议所需的要求；“禁止”表示不允许的行为；“建议”表示优先采用但允许有理由调整；“可选”表示按任务需要使用。步骤式指令和检查清单在适用时必须执行；标注为建议或可选的内容除外。用户明确覆盖的规则以用户指令为准。

## 核心规则

除非用户明确覆盖，否则必须遵守：

1. 每个并发修改代码的 Agent 必须拥有独立工作树。
2. 修改代码的 Agent 必须从分配的工作树根目录启动。
3. 持久报告和原始执行产物必须保存在可清理工作树之外的项目级 `agent-artifacts/` 目录。
4. 分别建模工作树与执行：工作树是操作位置，执行是一次有记录的活动。
5. 每次执行必须分配唯一且固定的目录；禁止用重试覆盖先前执行。
6. 每次已完成执行必须通过 `manifest.json` 绑定精确 Git commit。
7. 禁止并行 Agent 写入同一个汇总文件；必须指定唯一汇总者。
8. 必须保留失败和被拒绝的工作，以及相关证据和决策理由。
9. 工作树可清理，产物必须持久保留。
10. 代码状态和必需证据可恢复之前，禁止删除工作树。
11. 每个项目或专题协调范围必须恰有一名活跃编排者。
12. 每个被派发的执行者必须获得不可变的 `assignment.json`，明确路径、commit、权限、输入和必需输出。
13. 必须通过仓库本地 excludes 文件让 Git 忽略 `.agent-artifacts`；禁止为此修改全局 Git 配置。

## 概念模型

不需要专题的独立昇腾算子任务使用：

```text
任务
├── 工作树
│   └── 分支
│       └── commit
└── 执行
    ├── manifest.json
    ├── report.md
    ├── tests/
    ├── logs/
    ├── benchmarks/
    └── patches/
```

迭代型昇腾算子工程使用：

```text
项目
└── 专题
    ├── 参考资料
    ├── 基线（适用时）
    └── 方案
        └── 执行
            └── 产物
```

各层分别回答：

| 层次 | 必须表达的含义 |
|---|---|
| 项目 | 正在开发哪个昇腾算子系统或仓库？ |
| 专题 | 要实现什么昇腾算子目标，受哪些条件约束？ |
| 方案 | 正在验证哪一个具体设计、实现、移植或优化假设？ |
| 执行 | 具体进行了哪一次实现、测试、性能分析或基准测试？ |
| 产物 | 这次执行产生了哪些原始或派生证据？ |

方案表示一个具体假设或实现方式，不表示执行者或某次执行。执行表示对该方案开展的一次实现、测试、基准测试、审查或审计。一个方案可以包含多次执行，每次都有自己的合约和精确 commit。方案 ID 在整个专题内统一分配，禁止复用。新专题不再使用轮次（Round）的身份、目录或生命周期；比较和里程碑写入汇总，不通过轮次划分所有权。

执行控制流程：

```text
编排者
    -> 任务合约
    -> 工作树 + 执行
    -> 执行者
    -> 完成证据
    -> 编排者验收
    -> 下一角色或状态转换
```

## 项目布局

建议将工作树与持久产物放在同一项目容器目录下，互为同级目录：

```text
<project-container>/
├── <primary-worktree-name>/       # 现有主工作树；实际名称通过发现获得
├── worktrees/                    # 可清理的工作树
│   ├── codex-layernorm-tiling/
│   ├── claude-aicore-review/
│   └── matmul-ascend910b-v002/
└── agent-artifacts/              # 持久、共享，位于工作树之外
    ├── runs/                     # 非专题执行
    └── campaigns/                # 算子工程专题
```

默认顶层产物目录只有 `campaigns/` 和独立任务的 `runs/`。按需创建目录，禁止预先生成空目录骨架。需要项目级汇总或协调时，`summary/` 和 `registry/` 是可选扩展。

现有仓库布局不同时，保留原布局并确定对应的绝对路径。禁止假定仓库上级目录可写或可安全修改，必须先检查。

### 发现主工作树

主工作树可以使用任意目录名。禁止要求目录必须叫 `repo`、为匹配示例而重命名现有检出目录，或从分支名和远程 URL 推导路径。

派发前，编排者必须确定实际路径：

1. 从用户提供的仓库或工作树路径开始；当前目录位于目标仓库内时，也可从当前目录开始。若从项目容器启动，先检查现有布局并定位目标检出目录。存在多个可能的仓库时，向用户确认。
2. 使用 Git 元数据识别，不依赖目录名称：

```bash
git -C "<existing-worktree-path>" rev-parse --show-toplevel
git -C "<existing-worktree-path>" worktree list --porcelain
git -C "<existing-worktree-path>" rev-parse --path-format=absolute --git-common-dir
```

3. 从 Git 工作树清单中的主工作树条目识别主工作树，并核对共享 Git 元数据。当前目录可能是关联工作树，主工作树也不一定使用 `main` 分支。禁止将公共 Git 元数据目录当作代码工作树。裸仓库没有主代码工作树，必须记录其实际仓库路径并使用专用代码工作树。
4. 将发现的仓库绝对路径写入 `project.repository`，将分配的执行工作树路径写入 `project.worktree`。根据现有布局分别确定项目容器、工作树存放根目录和外部产物根目录，禁止通过拼接固定的 `repo` 目录名构造这些路径。
5. 保留已有目录名。无法安全识别目标仓库时，停止派发并请求其路径，禁止自行创建或假定存在 `repo` 目录。

禁止将共享 `agent-artifacts/` 存储放入可清理工作树。除非用户明确要求，否则禁止提交原始执行产物到 Git。

## Agent 启动目录

按角色选择启动位置：

| 角色 | 启动位置 |
|---|---|
| 编排者 | 项目容器根目录；无需代码工作树 |
| 昇腾算子编码、修复、重构执行者 | 分配的分支工作树根目录 |
| 昇腾算子实现执行者 | 分配的方案工作树根目录 |
| 测试者 | 固定在精确目标 commit 的 detached 工作树 |
| 审查者或审计者 | detached 只读工作树，或专用审查工作树 |
| 集成者 | 专用集成工作树 |
| 规划者或研究者 | 仅在保证只读时使用主仓库 |
| 产物汇总者 | 项目级 `agent-artifacts/` 上下文；无需代码工作树 |

启动时，修改代码前必须核实：

```text
当前目录 == 分配的工作树根目录
当前分支或 detached commit == 合约要求
Git 工作树根目录 == project.worktree
共享 Git 仓库 == project.repository
产物链接目标 == artifacts.root_directory（固定的项目产物根目录）
执行目录 == artifacts.run_directory
没有其他活跃 Agent 占用该工作树
```

编辑前必须读取适用的 `AGENTS.md`、`CLAUDE.md`、仓库说明和用户约束。

禁止从项目容器目录启动代码写入 Agent，因为它不是工作树。存在并行 Agent 时，建议避免从主工作树启动代码写入 Agent。

## 编排者职责

符合适用范围的昇腾算子任务跨越多个 Agent、工作树、执行、方案或生命周期阶段时，必须设置编排者。人工或确定性程序均可承担此角色；若由 Agent 承担，则从项目容器根目录启动。

编排者负责流程控制，不负责实现。必须执行：

- 发现真实的主仓库与分配工作树路径，不要求固定目录名；派发前检查仓库说明、活跃工作树、未提交状态、专题状态和当前汇总。
- 为任务、专题、方案、工作树、分支和执行分配无冲突的身份。
- 创建工作树前解析并记录精确基准 commit。
- 创建执行者的执行目录、不可变合约、初始 manifest 和 `.agent-artifacts` 上下文链接。
- 维护仓库本地的 `.agent-artifacts` Git 忽略规则，禁止修改全局 Git 配置或已提交的忽略文件。
- 派发时提供明确角色和固定合约路径。
- 通过 manifest 和报告监控状态，禁止仅根据进程或目录名推断进度。
- 在开始审计、集成、汇总、重试或清理前，验证终态输出。
- 执行失败、取消或被替代时，保留其来源与历史。

编排者禁止：

- 在项目容器或主工作树中修改业务源码。
- 让并发执行者复用同一个可写工作树。
- 派发后重写执行者的合约。
- 审计自己的实现结果，或默许证据不完整的结果通过。
- 在合约未明确授权时合并、删除分支、移除工作树或更新共享汇总。
- 在提示词、合约、manifest 或产物中放入秘密信息或凭据。

每个项目或专题协调范围只允许一名活跃编排者写入。所有权记录在 `agent-artifacts/registry/coordinator.json` 或等效的原子租约中。第二名编排者只有在负责不相交的范围，或完成明确的所有权交接后，才能操作。

建议编排者在 `agent-artifacts/runs/` 下保留自己的执行记录，将 `agent.role` 设为 `coordinator`。报告记录派发、验收、状态转换、未解决的阻塞项和最终交接。编排者执行不要求代码工作树。

编排者生命周期：

```text
initialized -> planning -> dispatching -> monitoring -> validating
                                      ├-> replanning -> dispatching
                                      ├-> blocked
                                      └-> closing -> completed -> archived
```

## Git 工作树协议

从明确的基准分支或 commit 创建新分支和工作树：

```bash
git -C "<primary-repository-absolute-path>" worktree add \
  -b agent/<agent>/<task-slug> \
  "<worktrees-root-absolute-path>/<agent>-<task-slug>" \
  <base-ref>
```

专题方案使用与工作类型匹配的分支前缀：

```bash
git -C "<primary-repository-absolute-path>" worktree add \
  -b <dev|opt|port|refactor>/<campaign>/v<variant>-<slug> \
  "<worktrees-root-absolute-path>/<campaign-short>-v<variant>" \
  <base-commit>
```

针对固定代码状态进行审查或测试时：

```bash
git -C "<primary-repository-absolute-path>" worktree add --detach \
  "<worktrees-root-absolute-path>/review-<target-short>" \
  <target-commit>
```

必须遵守以下防护要求：

- 创建工作树前解析 `<base-ref>` 或 `<target-commit>`。
- 禁止强制将同一分支检出到多个工作树。
- 禁止并发 Agent 共享同一个可写工作树。
- 禁止改变其他 Agent 的分支、工作树、文件或进行中的状态。
- 除非分配角色包含集成职责，否则禁止自动合并。
- 实现前记录基准 commit，完成后记录结果 commit。
- 重试必须创建新执行；只有所有权未变且明确允许时，才复用工作树。

## 工作树与执行分离

身份必须相互独立：

```text
worktree_id = 代码检出位置
run_id      = 一次执行及其证据
```

一个工作树可以承载多次顺序执行。一个方案可以在不同时期使用多个工作树。审查执行可以从另一个工作树检查实现者的结果 commit。

禁止仅用工作树名称标识执行。必须在 `manifest.json` 中明确记录关联：

```text
执行 -> 工作树路径
执行 -> 分支
执行 -> 基准 commit
执行 -> 结果 commit
执行 -> 专题/方案（适用时）
```

工作树生命周期：

```text
created -> active -> completed -> merged -> removed
                         └------> abandoned -> removed
```

执行状态为 `pending`、`running`、`completed`、`failed` 或 `cancelled`。执行状态与编排者验收、测试/审计结论、方案决策相互独立，详见“状态机”。归档和替代关系记录在外部，禁止覆盖终态 manifest。

执行记录通常比其工作树保留得更久。

## 持久产物访问

派发前必须创建项目产物根目录和准确的执行目录。每个工作树均使用相同的固定上下文映射：

```text
<worktree>/.agent-artifacts -> <project-container>/agent-artifacts/
```

禁止将此链接指向某个专题、方案或执行，也禁止在任务切换时重定向。执行者可通过根目录读取专题索引、参考资料、基线、其他方案及历史证据。读取权限不代表拥有这些文件的写入权。

不可变合约声明项目产物根目录 `artifacts.root_directory`、相对该根目录的 `artifacts.run_path` 和绝对执行目录 `artifacts.run_directory`。必须满足 `artifacts.root_directory / artifacts.run_path == artifacts.run_directory`；根目录本身不等于执行目录。必须将绝对执行目录传给每个产出持久证据的子进程；禁止根据 cwd、`latest` 链接或可变的“当前任务”指针推导输出位置。

无法使用符号链接时，将 `artifacts.entrypoint` 设为 `null` 并直接使用绝对路径。仅处理产物的执行者也可不使用链接和工作树。写入前必须验证真实路径；禁止用符号链接替换真实的用户目录。

执行者可在分配的工作树或获准的临时空间内自由使用 shell、构建工具、profiler、临时脚本和中间文件。合约约束持久交付物，不约束每个临时文件。提交前必须将支持结论的全部证据收集到分配的执行目录；复制工具输出时记录源位置和目标位置。执行目录之外的持久专题文档必须通过 `permissions.additional_writable_paths` 明确写入所有权。

执行者和所有产出文件的子进程停止前，禁止归档执行、复用工作树或切换启动指针。固定链接本身不能保证并发源码修改安全。

新执行的标准路径：

```text
独立任务：  agent-artifacts/runs/<run-id>/
专题级：    agent-artifacts/campaigns/<campaign>/runs/<run-id>/
方案级：    agent-artifacts/campaigns/<campaign>/variants/VNNN/runs/<run-id>/
```

专题级执行用于不归属某个具体方案的任务，例如汇总或准备参考资料。对具体方案开展的实现、测试和审计必须归入该方案。每次执行只有一个标准存储位置，索引只保存引用。

### 合约字段与实际目录名称

中文仅用于说明。目录和文件名称属于协议接口，必须保持原拼写、单复数及大小写；禁止将 `campaigns`、`variants`、`runs` 等翻译成中文路径，或改成 `campaign`、`variant`、`run`。新方案目录使用 `V001` 这类大写 ID，禁止改为分支名中的小写 `v001` 或追加方案描述；描述保存在 `name`。

下表中的 `/` 表示路径拼接，不是必须照抄的文本。实际值由编排者填写，禁止将字段名或示例占位符作为文件夹名：

| 合约字段或引用 | 对应位置与命名规则 |
|---|---|
| `project.repository` | 从 Git 元数据发现的主工作树或裸仓库绝对路径，不要求目录名为 `repo` |
| `project.worktree` | 分配的代码工作树绝对路径；仅处理产物的汇总角色可为 `null` |
| `artifacts.root_directory` | 项目产物根目录的实际绝对路径；默认名称为 `agent-artifacts` |
| `artifacts.entrypoint` | 工作树根目录的 `.agent-artifacts` 链接，目标为 `artifacts.root_directory`；无链接时为 `null` |
| `scope.campaign_directory` | `artifacts.root_directory / campaigns / scope.campaign_id`；非专题任务为 `null` |
| `scope.variant_directory` | `scope.campaign_directory / variants / scope.variant_id`；无具体方案时为 `null` |
| `artifacts.run_directory` | 方案级为 `scope.variant_directory / runs / artifacts.run_id`；专题级为 `scope.campaign_directory / runs / artifacts.run_id`；独立任务为 `artifacts.root_directory / runs / artifacts.run_id` |
| `artifacts.run_path` | 上述执行目录相对于项目产物根目录的路径；方案任务包含完整的 `campaigns/.../variants/VNNN/runs/...` 前缀 |
| `startup.assignment_file` | `artifacts.run_directory / assignment.json` |
| `startup.bootstrap_file` | `artifacts.run_directory / worker-start.md` |
| `startup.protocol_file` | `artifacts.run_directory / protocol / SKILL.md` |
| `required_outputs`、执行 manifest 的 `artifacts` 和 `result.evidence` | 相对此次执行目录，不相对于工作树、专题目录或项目产物根目录 |
| `inputs`、`reviewed_runs[].manifest_file` | 绝对文件路径，不根据当前目录推导 |
| 方案 manifest 的 `runs` | 相对于该方案目录的执行 manifest 路径，例如 `runs/test-01/manifest.json`；历史执行可使用绝对路径 |

专题资料目录保留 `reference/`、`baseline/`、`variants/`、`runs/`、`summary/` 名称；执行内部保留 `protocol/`、`logs/`、`tests/`、`benchmarks/`、`patches/`、`profiling/`、`attachments/`、`environment/` 名称。各目录仍按需创建。`protocol/` 内冻结的是 `SKILL.md`、`templates/`、`schemas/` 和 `scripts/`；禁止将协议模板目录与运行产物目录混为一谈。

### Git 忽略规则

创建 `.agent-artifacts` 前，编排者必须确保 Git 忽略以下准确的根目录模式：

```gitignore
/.agent-artifacts
```

禁止添加尾部斜杠：工作树入口通常是符号链接，仅针对目录的模式可能无法忽略它。

编排者直接维护仓库本地 excludes 文件。保留现有内容，仅在模式缺失时追加：

```bash
exclude_file="$(git rev-parse --path-format=absolute --git-path info/exclude)"
mkdir -p "$(dirname "$exclude_file")"
touch "$exclude_file"
grep -qxF '/.agent-artifacts' "$exclude_file" ||
  printf '%s\n' '/.agent-artifacts' >> "$exclude_file"
```

这是仓库本地的操作元数据，不提交到 Git，也不影响其他仓库。禁止为此使用 `git config --global`、修改全局 excludes 文件，或修改仓库已提交的 `.gitignore`。

创建符号链接后，从工作树根目录验证：

```bash
git check-ignore -v .agent-artifacts
```

若 `.agent-artifacts` 已被 Git 跟踪，必须停止并报告。未经明确授权，禁止从索引移除它或重写仓库历史。

## 任务合约协议

编排者必须在派发前，于准确的执行目录中创建 `assignment.json`。合约是任务的权威依据。使用 `templates/assignment.json`，填写全部占位符，并通过 `scripts/validate_contract.py` 校验。2.0 版本有意不兼容旧布局；历史合约继续使用各自冻结的 schema。

示例中的重复 `a` SHA 仅用于展示，派发前必须解析真实的完整 commit：

```json
{
  "schema_version": "2.0",
  "assignment_id": "V001-implementation-01",
  "created_at": "2026-09-21T10:00:00+08:00",
  "coordinator": {
    "name": "coordinator",
    "run_id": "20260921-coordinator-01"
  },
  "role": "implementation",
  "objective": "Implement FP16 RMSNorm for Ascend 910B.",
  "project": {
    "container": "/projects/rmsnorm",
    "repository": "/projects/rmsnorm/ascend-ops",
    "worktree": "/projects/rmsnorm/worktrees/rmsnorm-01"
  },
  "git": {
    "branch": "dev/rmsnorm-01/v001-reference",
    "base_commit": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "target_commit": null
  },
  "scope": {
    "campaign_id": "rmsnorm-01",
    "campaign_directory": "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01",
    "variant_id": "V001",
    "variant_directory": "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/variants/V001"
  },
  "artifacts": {
    "root_directory": "/projects/rmsnorm/agent-artifacts",
    "run_id": "rmsnorm-01",
    "entrypoint": ".agent-artifacts",
    "run_path": "campaigns/rmsnorm-01/variants/V001/runs/rmsnorm-01",
    "run_directory": "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/variants/V001/runs/rmsnorm-01"
  },
  "startup": {
    "working_directory": "/projects/rmsnorm/worktrees/rmsnorm-01",
    "assignment_file": "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/variants/V001/runs/rmsnorm-01/assignment.json",
    "bootstrap_file": "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/variants/V001/runs/rmsnorm-01/worker-start.md",
    "protocol_file": "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/variants/V001/runs/rmsnorm-01/protocol/SKILL.md"
  },
  "inputs": [
    "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/README.md",
    "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/manifest.json",
    "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/reference/specification.md",
    "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/reference/api-contract.md",
    "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/reference/oracle.md",
    "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/reference/acceptance.md",
    "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/summary/status.md",
    "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/variants/V001/plan.md"
  ],
  "required_outputs": [
    "manifest.json",
    "report.md",
    "tests/correctness.json",
    "patches/final.diff"
  ],
  "verification": [
    "Record a clean result commit and test that exact commit",
    "Record unsupported shapes and unexecuted gates"
  ],
  "reviewed_runs": [],
  "permissions": {
    "modify_source": true,
    "merge": false,
    "remove_worktree": false,
    "update_summary": false,
    "additional_writable_paths": []
  },
  "supersedes": null
}
```

合约规则：

- 所有目录、启动文件、`inputs` 和 `reviewed_runs[].manifest_file` 必须使用规范化的本机绝对路径。当前实现支持 Linux 和 macOS 的 POSIX 路径。远程执行路径必须在派发前明确解析。
- 从 Git 元数据发现 `project.repository`。代码角色的 `project.worktree` 和 `startup.working_directory` 指向分配的检出目录；仅处理产物的汇总角色可将工作目录设为产物根目录，并使用 `worktree: null`。
- `scope` 记录专题与方案 ID 及其准确目录。独立任务将全部 scope 字段设为 `null`；专题级任务将方案字段设为 `null`。
- `artifacts.entrypoint` 为 `.agent-artifacts` 或 `null`。存在入口时，其目标始终为 `artifacts.root_directory`。`run_path` 相对于该项目产物根目录，不相对于专题或方案。
- `required_outputs` 全部使用相对此次执行目录的路径。禁止使用 `..`、绝对输出路径或越界符号链接来表示其他位置的产物。
- `inputs` 列出执行者必须读取的文件，按角色纳入专题 README/索引、参考与验收文件、当前汇总、适用基线，以及方案计划和前序结论。编排者必须在派发前准备好这些文件。执行期间可能变化的验收输入必须保存快照或版本，禁止无记录地改变已分配的标准。
- `reviewed_runs` 通过绝对路径、执行 ID 和 SHA-256 固定每个被审查的终态 manifest。审计合约必须列出其评估的测试/基准测试执行。仅审查代码的任务可在范围明确时使用空列表，但禁止声称已审计未检查的测量结果。
- `git.base_commit` 是精确起点。测试、基准测试、审查和审计角色还必须提供 `git.target_commit`；检出从此目标开始，它可以不同于实现最初的基准 commit。只有集成角色可获得 `merge` 权限；只读检查角色禁止修改实现。
- `permissions.additional_writable_paths` 列出本执行者额外拥有的专题文档的准确路径。完整专题仍可读取。禁止通过命令白名单限制工具选择和临时实验方式。
- `supersedes` 为被替代执行的 manifest 绝对路径，或 `null`。禁止向已归档执行回写替代指针。
- 派发后冻结合约、启动文件和协议快照。修正必须创建新合约和新执行；禁止用修订后的合约重新解释旧执行。
- 禁止包含秘密信息或未经脱敏的环境变量值。

### 执行者启动引导

新 Agent 不会继承编排者已加载的 Skill 或对话。派发前，编排者必须：

1. 将当前 `SKILL.md`、`templates/`、`schemas/` 和 `scripts/` 复制到 `<run_directory>/protocol/`，并冻结此次执行的协议快照。禁止复制 Git 元数据、凭据和无关文件。
2. 将 `templates/worker-start.md` 渲染到 `startup.bootstrap_file`。根据合约替换全部占位符，包括合约/协议/工作树/产物的绝对路径、专题与方案信息、链接映射、必读文件和具体输出位置。不存在的专题、方案、工作树或链接字段用 `not applicable` 表示。启动引导是合约的展示，不是另一份权威来源。
3. 将“首先读取合约”的要求写入启动提示词，禁止只放在执行者尚未读取的文件中：

```text
首先读取 <absolute-assignment-file>，再读取 <absolute-bootstrap-file>。
执行任务命令或修改文件前，阅读必需说明和输入，核实目录与链接映射，
回报合约 ID、专题、方案、执行身份，以及全部产物的准确目标路径。
禁止猜测替代路径。
```

4. 在 `startup.working_directory` 启动执行者。人工启动时提供准确目录和同样的首条指令。环境变量仅为可选辅助；使用时，`AGENT_ASSIGNMENT`、`AGENT_ARTIFACT_ROOT` 和 `AGENT_RUN_DIR` 必须填入合约给定的绝对路径。
5. 阅读执行者的启动确认，并在接受实现交接前与合约核对。启动期间允许读取文件和只读检查；源码编辑与实验必须等启动前检查通过后再开始。

原生 Skill 发现机制可作为补充，但禁止替代明确的启动提示。必须保留仓库现有说明，禁止覆盖说明文件或 Agent 全局设置。复用工作树时，先停止旧执行及其产物生成进程，保留固定的产物根目录链接，再传入新合约的准确路径。禁止通过扫描“最新执行”寻找合约。

### 执行者启动前握手

执行者首先读取合约、启动引导、冻结的协议、适用仓库说明和必需 `inputs`，必须理解：

- 专题：共享的昇腾算子目标、参考资料、基线和验收约束。
- 方案（`V`）：专题中的具体实现方式或假设；ID 在专题内唯一，不表示 Agent 或某次执行。
- 执行：本次分配的活动，有独立角色、commit 和持久证据。
- 其他方案及其历史失败属于可读上下文；未获得所有权时禁止修改相关文件。

随后核实并回报实际值，不能只回复“已阅读协议”：

- 合约 ID、角色、专题/方案/执行 ID，以及解析后的合约与协议路径。
- 工作目录、工作树根目录、共享 Git 仓库身份，以及分支/基准 commit 或 detached 目标 commit。仅处理产物的汇总角色必须将不适用的工作树/Git 检出检查记为 `not_applicable` 并说明理由。
- 产物根目录、专题目录、方案目录、执行目录，以及每个必需输出的绝对路径。
- 实际 `.agent-artifacts` 链接及其解析后的项目产物根目录；若 `entrypoint` 为 `null`，则核实声明的绝对路径替代方式。
- 必需输入可读、声明的外部目标位置可写，且没有其他活跃执行者占用工作树。

将检查结果写入 `manifest.preflight`，记录 `status`、时间戳和解析后的路径，之后才能从 `pending` 转为 `running`。存在不一致时，通过已验证的执行路径记录失败，并在修改源码前停止；若连目标路径也不可信，则直接向编排者报告，禁止通过可疑链接写入。

### 所有权与完成握手

```text
编排者创建冻结的合约/启动引导/协议，以及 pending manifest
    -> 执行者读取、验证、确认，并接管进行中的执行文件
    -> 执行者在分配的源码与所有权边界内自由探索
    -> 执行者收集持久产物、停止产物生成进程、提交终态文件
    -> 编排者检查实际文件并写入 validation.json
    -> 专题决策负责人根据验证后的测试/审计证据决定接受或拒绝
```

执行者探索期间可使用临时输出。提交前必须收集持久证据、记录精确结果 commit、报告未执行的验证与缺失输出，并将执行状态设为 `completed`、`failed` 或 `cancelled`。`completed` 仅表示分配的执行已结束，不表示测试通过或方案已被接受。执行者禁止自行将编排者验收标为通过。提交时冻结执行证据；编排者随后添加其拥有的 `validation.json` 或终止记录，不修改执行者文件。

`validation.json` 初始状态为 `pending`。编排者检查合约身份、启动确认、所有权、实际输出路径与文件、证据和 commit 的来源关联、manifest/报告一致性，以及产物生成进程是否停止。各项结果设为 `passed`、`failed` 或 `not_applicable`；不适用项必须说明理由。只有全部必需检查通过，总体状态才能为 `passed`，否则为 `needs_repair`。缺少必需输出不能仅凭解释就通过。在审计或集成前，可说明理由后暂缓清理就绪检查；删除前必须重新检查可恢复性。

使用下方校验器检查结构和路径证据，再独立审查命令、测试覆盖、原始结果、环境和结论。校验器不判断数值正确性、审计独立性、进程终止或业务验收。本协议提供交接门禁，不提供操作系统沙箱或命令白名单。

执行者的一次回复不能独立关闭任务。验收失败必须阻止接受、合并和清理；编排者可向同一执行者派发修复或诊断执行。已提交执行保持冻结；新测试、证据恢复、修正和重试使用新执行，通过 `supersedes` 引用旧 manifest。禁止覆盖原始证据。尚未提交时，活跃执行者可在同一次执行中补齐自己缺失的输出。

执行者崩溃时，必须确认它及其产物生成子进程均已停止，撤销所有权，保留部分文件，并写入编排者拥有的终止/验收记录。禁止伪造执行者报告或静默覆盖其未完成 manifest。重试使用新执行。只要仍可能有进程写入，就禁止归档或清理。

### 可执行合约检查

检查已有执行时，使用该执行冻结的协议包：

```bash
uv run --no-project --with 'jsonschema[format]==4.26.0' python <protocol>/scripts/validate_contract.py <assignment.json>
uv run --no-project --with 'jsonschema[format]==4.26.0' python <protocol>/scripts/validate_contract.py <assignment.json> --check-files
uv run --no-project --with 'jsonschema[format]==4.26.0' python <protocol>/scripts/validate_contract.py <assignment.json> --manifest <manifest.json> --check-files
```

第一条命令检查 schema 和标准路径关系；第二条增加启动文件、链接和输入存在性检查；第三条还检查终态交接的必需输出、证据路径、被审查 manifest 的摘要、身份、角色和 commit 一致性。格式检查必须显式启用，并安装相应可选依赖。模板有意保留占位符，填写完成前禁止派发。

## 标准执行目录

按生命周期阶段创建文件：派发时创建合约、启动引导和协议快照；执行创建时生成 manifest；提交时生成报告；编排者验收时生成 validation。可选证据目录按需创建：

```text
<run-id>/
├── assignment.json              # 不可变的派发输入
├── worker-start.md              # 已填充的启动说明
├── protocol/                    # 冻结的 Skill、schema、模板和校验器
├── manifest.json                # 必需的机器可读身份与状态
├── report.md                    # 必需的人类可读结果报告
├── validation.json              # 编排者完成验收
├── logs/                        # 命令、构建、profiler 和运行日志
├── tests/                       # 测试输出与正确性证据
├── benchmarks/                  # 原始性能数据与汇总
├── patches/                     # 复现或恢复补丁
├── profiling/                   # profiler 原生文件与导出文件
├── attachments/                 # 截图或辅助文件
└── environment/                 # 环境与依赖快照
```

仅创建需要的可选目录，并统一使用以上名称。原始数据与结论必须分开保存。

示例：

```text
tests/pytest.txt
tests/correctness.json
benchmarks/latency.json
benchmarks/summary.csv
logs/build.log
logs/stdout.log
profiling/msprof/
patches/final.diff
environment/system.json
```

禁止在产物中保存凭据、token、私钥、个人数据或含秘密信息的环境变量值。

## 执行清单 `manifest.json`

派发给执行者的执行使用 `templates/run-manifest.json` 和 `schemas/run-manifest.schema.json`。编排者的编排记录单独保存，不必伪装成执行者合约。时间戳采用带时区的 ISO 8601，Git commit 使用精确完整值，未知结果使用 `null`。

示例中的 SHA 仅用于展示：

```json
{
  "schema_version": "2.0",
  "run_id": "rmsnorm-01",
  "assignment_file": "assignment.json",
  "agent": {
    "name": "codex",
    "role": "implementation"
  },
  "status": "completed",
  "preflight": {
    "status": "passed",
    "assignment_id": "V001-implementation-01",
    "checked_at": "2026-09-21T10:01:00+08:00",
    "assignment_file": "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/variants/V001/runs/rmsnorm-01/assignment.json",
    "protocol_file": "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/variants/V001/runs/rmsnorm-01/protocol/SKILL.md",
    "root_directory": "/projects/rmsnorm/agent-artifacts",
    "run_directory": "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/variants/V001/runs/rmsnorm-01",
    "required_output_destinations": [
      "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/variants/V001/runs/rmsnorm-01/manifest.json",
      "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/variants/V001/runs/rmsnorm-01/report.md",
      "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/variants/V001/runs/rmsnorm-01/tests/correctness.json",
      "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/variants/V001/runs/rmsnorm-01/patches/final.diff"
    ],
    "working_directory": "/projects/rmsnorm/worktrees/rmsnorm-01",
    "repository": "/projects/rmsnorm/ascend-ops",
    "worktree": "/projects/rmsnorm/worktrees/rmsnorm-01",
    "campaign_id": "rmsnorm-01",
    "campaign_directory": "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01",
    "variant_id": "V001",
    "variant_directory": "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/variants/V001",
    "run_id": "rmsnorm-01",
    "artifact_link_target": "/projects/rmsnorm/agent-artifacts",
    "read_inputs": [
      "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/README.md",
      "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/manifest.json",
      "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/reference/specification.md",
      "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/reference/api-contract.md",
      "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/reference/oracle.md",
      "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/reference/acceptance.md",
      "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/summary/status.md",
      "/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/variants/V001/plan.md"
    ]
  },
  "timestamps": {
    "created_at": "2026-09-21T10:00:00+08:00",
    "started_at": "2026-09-21T10:01:00+08:00",
    "finished_at": "2026-09-21T11:00:00+08:00"
  },
  "scope": {
    "campaign_id": "rmsnorm-01",
    "variant_id": "V001"
  },
  "git": {
    "branch": "dev/rmsnorm-01/v001-reference",
    "base_commit": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "target_commit": null,
    "worktree": "/projects/rmsnorm/worktrees/rmsnorm-01",
    "result_commit": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
  },
  "reviewed_runs": [],
  "result": null,
  "artifacts": [
    "report.md",
    "tests/correctness.json",
    "patches/final.diff"
  ],
  "supersedes": null,
  "risks": [],
  "unfinished": []
}
```

Manifest 要求：

- `assignment_file` 固定为 `assignment.json`；身份、角色、范围、Git 起始/目标 commit 和工作树必须与合约一致。
- `artifacts` 和 `result.evidence` 使用执行目录相对路径。`reviewed_runs` 使用合约中固定的输入 manifest 绝对路径。其他执行的引用属于输入，不是需要复制的输出文件。
- `result_commit` 标识已提交的实现/集成结果。只读测试和审查角色使用 `target_commit`，并将 `result_commit` 留为 `null`。
- 声称验证了结果 commit 时，必须在该 commit 的干净工作树上测试，或保留精确源码快照并证明它与记录的 commit 一致。必须记录命令、源码状态、构建二进制的来源、环境和原始输出。禁止将有未提交修改的探索性测量直接视为最终 commit 的证据。
- 保留执行时间戳和终态。归档、后续决策与替代关系写入编排者记录或索引；禁止修改旧 manifest 来设置 `superseded_by`，或将原结果覆盖为 `archived`。
- 重复执行必须创建新执行。代码变化后，旧结论不再自动适用于新 commit；旧结论保留为历史。

## 测试、基准测试和审计结果

必须区分三类独立状态：

| 层次 | 取值 | 负责人及含义 |
|---|---|---|
| 执行状态 | `pending`、`running`、`completed`、`failed`、`cancelled` | 执行者：本次执行是否结束？ |
| 验证结论 | 下方按角色定义 | 测试/基准测试/审计执行者：证据支持什么结论？ |
| 方案决策 | `accepted`、`rejected`、`needs_revision`、`superseded`、`final`、`cancelled` | 决策负责人：是否采用这个精确实现？ |

编排者验收状态为 `pending`、`passed`、`needs_repair`，检查交接完整性和来源关联，不等同于正确性结论或方案决策。记录完整的失败测试可以通过交接验收，同时阻止方案被接受。

每次测试或审计都在 `variants/VNNN/runs/<run-id>/` 下保留独立合约、执行记录、manifest、报告和原始证据。下方示例是合并到通用模型中的角色专用 manifest 片段，不是独立完整的 manifest：

```json
{
  "agent": {"name": "tester", "role": "test"},
  "status": "completed",
  "git": {"target_commit": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", "result_commit": null},
  "result": {
    "verdict": "failed",
    "passed": 118,
    "failed": 2,
    "skipped": 4,
    "evidence": ["tests/results.json", "logs/test.log"]
  }
}
```

测试结论使用 `passed`、`failed` 或 `inconclusive`。即使执行正常结束，只要存在测试用例失败，结论就是 `failed`。基础设施故障、覆盖不足或硬件不可用都不能暗示通过。必须记录 `skipped` 数量以及各验收项跳过的原因，由验收合约决定是否允许跳过。没有执行测试的记录禁止标记为通过。

基准测试结论使用 `valid`、`invalid` 或 `inconclusive`，表示测量是否有效，不表示时延是否达到验收目标。必须在 `result` 及其证据文件中保存指标、单位、shape、计时方法、环境和原始测量值。

```json
{
  "agent": {"name": "auditor", "role": "audit"},
  "status": "completed",
  "git": {"target_commit": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", "result_commit": null},
  "reviewed_runs": ["/projects/rmsnorm/agent-artifacts/campaigns/rmsnorm-01/variants/V001/runs/test-01/manifest.json"],
  "result": {
    "verdict": "invalid",
    "blocking_findings": 1,
    "evidence": ["findings.json", "report.md"]
  }
}
```

审查/审计结论使用 `valid`、`valid_with_caveats`、`invalid` 或 `inconclusive`。每条问题记录必须包含固定 ID、严重程度、具体判断、代码/证据引用和后续要求。审计通过合约中的摘要固定被审查终态 manifest，并在结果 manifest 中列出相同的绝对路径。目标实现的测试/性能证据必须与 `target_commit` 一致。基线或对比执行可以使用其他 commit，但必须在输入和报告中明确标为比较对象，禁止冒充目标证据。

验收必须使用独立审计者。实现者自检是有用证据，但不能满足独立审计要求。缺少独立审计角色时，必须记录验收项未完成，禁止静默自行批准。

只有指定负责人可以更新方案的 `result.md`、`audit.md`、`decision.md` 和 manifest。每份汇总必须指明精确目标 commit 和支持它的执行；修订时保留带日期的历史结论。两次执行结论不一致时，必须呈现差异，直到问题解决。新测试或审查禁止覆盖旧执行结果；实现更新后，必须获得适用于新代码的验证才能被接受。

## 执行报告 `report.md`

使用以下模板：

```markdown
# 执行报告

## 目标

说明分配的目标。

## 上下文

- 基准引用或 commit：
- 分支：
- 工作树：
- Agent 与角色：

## 结果概述

描述实际执行过程和最终结果。

## 修改

列出源码修改和相关 commit SHA。只读执行填写“无”。

## 验证

逐项列出命令或步骤、结果和产物路径，明确哪些验证未执行。

## 性能

汇总基准测试结果并链接原始文件。未测量时填写“未测量”。

## 偏差

解释与合约或计划不一致的部分。

## 风险与限制

记录已知风险、不确定性、环境限制和覆盖缺口。

## 未完成工作

列出剩余事项，无则填写“无”。

## 交接

说明下一负责人、建议动作和待检查的精确 commit。
```

禁止将大量日志直接粘贴到报告中。必须总结并引用原始产物。

## 算子工程专题布局

```text
agent-artifacts/campaigns/<campaign>/
├── README.md                    # 目标、目录和上下文索引
├── manifest.json                # 专题状态与方案索引
├── reference/                   # 规格、API、正确性依据、验收标准、测试夹具
├── baseline/                    # 仅在有意义时建立
├── variants/
│   ├── V001/
│   │   ├── manifest.json        # 演进关系、对比对象、commit 和执行引用
│   │   ├── hypothesis.md
│   │   ├── proposal.md
│   │   ├── plan.md
│   │   ├── implementation.md
│   │   ├── result.md            # 针对精确 commit 的测试/性能汇总
│   │   ├── audit.md             # 独立审计汇总
│   │   ├── decision.md
│   │   └── runs/
│   │       ├── <implementation-run-id>/
│   │       ├── <test-run-id>/
│   │       └── <audit-run-id>/
│   └── V002/
├── runs/                        # 不归属具体方案的专题级执行
└── summary/
    ├── status.md
    ├── timeline.md
    ├── comparison.md
    ├── decisions.md
    └── final-report.md          # 仅在收尾时创建
```

按需创建目录。专题 README/manifest 帮助执行者发现完整专题，启动输入明确其中必须读取的部分。历史原始日志可按需打开。每个新方案执行都嵌套在其方案目录下。工作树链接指向项目产物根目录，禁止指向上图中的专题目录。

每个专题必须包含 `reference/`。只有比较有意义时才建立 `baseline/`，禁止为新算子编造基线测量值。

### 兼容现有专题

2.0 版本移除 Round，并改变上下文链接目标及方案执行的标准路径。历史合约、执行、协议快照、分支和证据必须保留原路径，读取时使用其保留的 schema。禁止重命名旧记录或重写内嵌引用。

切换工作树前，必须停止所有旧执行者及其产物生成进程。旧任务仍活跃时，使用新工作树，禁止重定向旧链接。新工作采用 v2 合约与路径，旧方案和旧执行通过明确的绝对路径引用建立索引。分配新方案 ID 前，必须预留专题内已有的所有 V ID；若历史 ID 只在轮次内唯一，则为继续推进的方案分配新的专题级唯一 ID，并保留明确的新旧映射。禁止追溯重编历史编号。

方案汇总保留带日期的决策和事实修正。提交后的执行证据保持不可变，后续决策与归档记录在专题索引中。

## 专题定义

`README.md` 定义稳定目标，不逐项罗列每个实验。首先声明一种专题类型：

```text
new-development
optimization
porting
refactor
validation
```

随后包含：

```markdown
# <专题标题>

## 目标

定义算子能力或工程目标；适用时加入目标指标。

## 范围

明确昇腾算子、语义、API、负载、shape、数据类型、布局、CANN 或框架接入路径，以及支持的昇腾硬件。

## 约束

定义正确性容差、确定性、内存、兼容性和可维护性限制。

## 参考资料与正确性判定依据

明确权威规格、行为判定依据、测试夹具和数值容差。

## 基线（适用时）

记录基线 commit 和主要指标。

## 成功标准

定义功能完整性、API 兼容性、正确性、性能、可移植性和审计验收要求。

## 排除项

说明明确不属于本专题的内容。
```

专题 `manifest.json` 建议包含：

```json
{
  "schema_version": "2.0",
  "campaign_id": "fused-rmsnorm-fp16-ascend910b",
  "title": "Fused RMSNorm FP16 Operator for Ascend 910B",
  "campaign_type": "new-development",
  "status": "active",
  "created_at": "2026-09-09T10:00:00+08:00",
  "updated_at": "2026-09-09T15:30:00+08:00",
  "goal": {
    "outcome": "Implement a production-ready fused RMSNorm operator.",
    "primary_metric": "p50_latency_ms",
    "target": 0.08,
    "direction": "lower"
  },
  "reference": {
    "specification": "reference/specification.md",
    "api_contract": "reference/api-contract.md",
    "oracle": "reference/oracle.md",
    "acceptance": "reference/acceptance.md"
  },
  "baseline": null,
  "current_selection": {
    "variant_id": "V003",
    "commit": "<full-sha>",
    "readiness": "validation"
  },
  "variants": [
    "variants/V001/manifest.json",
    "variants/V002/manifest.json",
    "variants/V003/manifest.json"
  ]
}
```

## 参考资料与基线协议

实现或接受任何方案前，必须建立并审查参考资料包，记录：

- 算子语义、数学定义、数据类型、布局、广播、别名、可变性和错误行为。
- API 与 ABI 合约，包括 shape、属性、输出、分发规则和接入点。
- 正确性判定依据，例如框架实现、标量模型、数学参考、标准测试向量或差分测试目标。
- 数值容差，以及它随数据类型、shape、累加模式或硬件变化的方式。
- 必需测试夹具、边界情况、无效输入、确定性要求和不支持的行为。
- 功能、性能、兼容性、文档和集成验收项。

按专题类型确定基线要求：

| 专题类型 | 必需的比较依据 |
|---|---|
| `new-development` | 参考资料/正确性依据及明确验收目标；基线可为 `null` |
| `optimization` | 现有实现的精确 commit，以及已审计的性能基线 |
| `porting` | 源后端行为及昇腾目标验收标准；有意义时建立性能基线 |
| `refactor` | 精确的行为/正确性基线及性能不回退阈值 |
| `validation` | 被验证实现的 commit，以及声明的预期行为或指标 |

适用基线时，必须在接受比较性结论前建立并审计基线，记录：

- 精确基线 commit，以及工作树是否干净。
- 昇腾硬件型号、SoC 版本、固件、驱动、CANN 工具包/运行时/编译器、构建参数、电源模式和频率策略。
- 操作系统、相关库、已去除秘密信息的环境变量，以及依赖版本。
- 输入 shape、数据类型、布局、分布、随机种子、预热次数、测量次数、同步方式和计时方式。
- 正确性判定依据、容差、确定性要求和测试覆盖。
- P50、P90 或 P95、P99、吞吐、内存及其他专题指标。
- 原始基准测试与性能分析文件。

`baseline/benchmark.md` 保存人类可读的解释，`baseline/benchmark.json` 保存机器可读的数据来源。禁止凭记忆补出缺失的原始基线数据。对于 `new-development`，记录 `baseline: null`；在建立有效的内部性能基线前，依据正确性判定标准和验收目标评价实现。

环境发生实质变化时，必须重新建立基线，或将跨环境比较标为无效。

## 方案身份与演进

在整个专题内统一分配 `V001`、`V002` 等唯一 ID。方案表示一个假设或具体实现方式，不表示时间窗口或执行者。机制描述保存在 `name` 中，目录名保持为固定的 `variants/VNNN/`。

使用 `parent_variant` 记录演进来源，`base_commit` 记录精确源码起点，`comparison_variants` 记录比较对象。演进来源不等同于比较对象。无父方案时使用 `null`，无比较对象时使用空列表。

多个方案及其执行可以并发推进。重试、新测量或审查在同一方案下创建新执行。假设或设计发生实质变化时，由编排者分配新方案。同一假设下的细化可以在已有方案中产生新 commit，但之前的测试和审计不能证明新 commit 已通过验证。

专题汇总可以比较任意方案集合并记录带日期的里程碑，无需引入 Round ID、共享“当前执行”或移动目录。

## 方案记录链

每个已实现方案必须保留以下记录链：

```text
hypothesis
    -> proposal
    -> plan
    -> implementation
    -> result
    -> audit
    -> decision
```

禁止将这些记录合并成一份文档。它们分别表达不同判断，使实际偏差可审计。若实现前取消，或任务仅做验证，必须将未执行阶段明确记为 `not_applicable` 并说明原因，禁止为补齐记录链而编造实现或结果。

### `hypothesis.md`：假设

记录：

- 观察与证据。
- 推测的因果机制。
- 可被证伪的预测。
- 预期指标范围。
- 假设应当不成立的条件。

### `proposal.md`：提案

记录：

- 提议的设计、算法、实现、移植、重构或优化，以及它与假设的关系。
- 相对于验收标准、当前选定方案及适用基线的预期收益。
- 兼容性与范围。
- 考虑过的替代方案。
- 风险、前提假设和拒绝标准。

区分：假设是可验证的判断，提案是选择开展的实验。

### `plan.md`：计划

记录：

- 具体实现步骤。
- 预计修改的文件或组件。
- 正确性测试矩阵。
- 基准测试和性能分析方法。
- 回滚或恢复方法。
- 所需 Agent 及角色边界。
- 完成与审计验收项。

区分：提案说明“为什么做、做什么”，计划说明“怎么做”。

### `implementation.md`：实现

记录：

- 分支、工作树、基准 commit 和结果 commit。
- 实际源码修改。
- 重要设计选择。
- 与计划的偏差及原因。
- 构建或环境变化。
- 已知实现限制。

未经检查最终 diff 或 commit，禁止声称计划中的工作已经实现。

### `result.md`：结果

报告观测结果，不在此作出接受决定。包含：

```markdown
# 结果

## 正确性

- 状态：
- 判定依据：
- 最大误差：
- 覆盖范围：

## 规格与集成

- API/ABI 符合性：
- 支持的 shape、类型、布局及昇腾硬件：
- 框架或运行时集成：
- 不支持或未完成的行为：

## 性能

| 指标 | 验收目标 | 基线（如有） | 当前选定方案 | 本方案 |
|---|---:|---:|---:|---:|

## 改善幅度

- 相对于验收目标：
- 相对于基线（如有）：
- 相对于当前选定方案：

## 环境

说明是否与参考或对比环境一致，并引用环境产物。

## 原始证据

列出执行 ID 和产物路径。

## 异常

记录波动、回退和未解释的现象。
```

优化和重构专题在原始基线与当前选定方案均有效时，必须同时与两者比较。新开发专题首先报告正确性依据符合情况和验收项状态；只有方法有效时，才与性能目标或参考实现比较。没有适用基线时，注明“不适用”或“不可比较”，禁止编造基线。

### `audit.md`：审计

验收审计必须由未参与该方案实现的审计者承担，自检记录单独保留。审计内容包括：

- 正确性、数值稳定性、确定性、未定义行为、数据竞争和边界情况。
- 测试覆盖和输入代表性。
- 预热、同步、迭代次数、缓存影响、频率策略、波动、异常值和统计置信度。
- 根据已记录 commit 和环境进行复现的可行性。
- 昇腾硬件、固件、驱动、CANN、框架和软件兼容性。
- 内存消耗、可维护性和运行风险。
- 报告中的表格是否与原始产物一致。

使用明确结论：

```text
valid
valid_with_caveats
invalid
inconclusive
```

性能数据优异并不足以证明算子有效。功能完整性、规格符合性、正确性、集成和兼容性仍是独立验收项。

### `decision.md`：决策

每个已启动方案最终必须有终态决策。`needs_revision` 是需要后续行动的中间决策，不表示结束：

```markdown
# 决策

状态：ACCEPTED | REJECTED | NEEDS_REVISION | SUPERSEDED | FINAL | CANCELLED

## 理由

根据已审计证据说明决定。

## 选定 commit

记录精确 commit，无则填写“无”。

## 有用发现

保留所得经验，尤其是失败方案中的发现。

## 动作

说明合并、继续推进、回滚或归档动作。

## 后续

说明下一个问题，无则填写“无”。
```

禁止只记录 `failed`。必须说明尝试了什么、为什么无效、哪些部分有用，以及下一步应尝试什么。

## 方案清单 `manifest.json`

在叙述性文档之外维护简洁的机器可读索引：

```json
{
  "schema_version": "2.0",
  "variant_id": "V003",
  "name": "single-pass-vector-reduction",
  "status": "superseded",
  "campaign_id": "fused-rmsnorm-fp16-ascend910b",
  "branch": "dev/fused-rmsnorm-fp16-ascend910b/v003-single-pass-vector-reduction",
  "base_commit": "<full-sha>",
  "result_commit": "<full-sha>",
  "runs": [
    "runs/20260909-143012-codex-single-pass-vector-reduction-01/manifest.json",
    "runs/20260909-151820-claude-audit-01/manifest.json"
  ],
  "requirements": {
    "specification": "passed",
    "correctness": "passed",
    "integration": "passed"
  },
  "metrics": {
    "p50_latency_ms": 0.078,
    "meets_target": true,
    "improvement_vs_baseline_percent": null
  },
  "audit_verdict": "valid",
  "decision": "superseded",
  "reason": "Meets the functional contract and target latency, but is superseded by a simpler accepted variant.",
  "parent_variant": "V001",
  "comparison_variants": [
    "V001",
    "V002"
  ]
}
```

v2 方案 manifest 中的所有 `runs` 引用均相对于该方案目录，并指向执行 manifest。其他位置的历史执行使用明确绝对路径引用。叙述性文档仍是推理与理由的权威来源，manifest 为自动化与看板提供索引。

## 汇总协议

方案执行和专题级 `runs/` 保存证据历史，`summary/` 保存当前专题知识，其中时间线和决策记录只追加。只有指定汇总者可以更新共享汇总文件。

### `summary/status.md`

保持简短，便于恢复工作时优先阅读。包含：

- 专题状态、未解决问题和活跃方案。
- 当前最佳方案及精确 commit。
- 参考资料版本、验收状态、当前选择、目标，以及适用时的基线或总体收益。
- 正确性与审计状态。
- 当前瓶颈。
- 活跃方案及负责人。
- 下一动作与阻塞项。

### `summary/timeline.md`

追加带日期的里程碑：

```text
timestamp | variant | event | commit | run | outcome
```

禁止为了匹配当前结论而重写历史。

### `summary/comparison.md`

维护覆盖全部方案的统一比较表：

```markdown
| 方案 | commit | 规格 | 正确性 | 集成 | 主要指标 | 相对目标 | 相对基线 | 审计 | 决策 |
|---|---|---|---|---|---:|---:|---:|---|---|
```

使用一致的单位和比较方向。无效比较必须明确标记，禁止强行归入同一口径。

### `summary/decisions.md`

维护简明决策记录：

```markdown
## DNNN — <决策>

- 日期：
- 状态：accepted | rejected | superseded
- 证据：<方案和执行引用>
- 理由：
- 影响：
```

既记录采用的技术，也记录明确不采用某项技术的决定。

### `summary/final-report.md`

仅在专题完成或明确关闭时创建。包含：

- 目标、范围、约束和成功标准。
- 参考规格、正确性判定依据和验收标准。
- 适用时的基线 commit、环境和测量结果。
- 按方案演进关系和带日期里程碑梳理的工程过程。
- 关键的已接受和已拒绝假设。
- 最终实现及精确 commit。
- 最终正确性与经过审计的性能。
- 支持的昇腾硬件和负载范围。
- 已知风险与限制。
- 复现步骤和产物索引。
- 未解决问题与后续方向。

最终报告是专题的主要交接文档，不能替代原始证据。

## 命名约定

短名称使用小写 ASCII kebab-case。避免空格、`latest` 等可变标签，以及 `final2` 等名称。

### 分支

一般实现任务：

```text
agent/<agent>/<task-slug>
```

昇腾算子专题实现：

```text
dev/<campaign>/vNNN-<variant-slug>
opt/<campaign>/vNNN-<variant-slug>
port/<campaign>/vNNN-<variant-slug>
refactor/<campaign>/vNNN-<variant-slug>
```

审查或审计需要分支时：

```text
review/<campaign>/vNNN-<scope>
```

示例：

```text
agent/codex/layernorm-tiling
agent/claude/aicore-audit
dev/fused-rmsnorm-fp16-ascend910b/v001-two-pass-reference
opt/matmul-fp16-ascend910b/v002-double-buffering
port/layernorm-ascend910b/v001-vector-core
review/matmul-fp16-ascend910b/v002-correctness
```

### 工作树

使用简短、可读且能对应分支的名称：

```text
<agent>-<task-slug>
<campaign-short>-vNNN
review-<target-short>
integration-<project-short>
```

### 专题和方案

```text
campaign: <operator-or-area>-<dtype-or-target>
variant:  VNNN
```

示例：

```text
matmul-fp16-ascend910b
flash-attention-ascend910b
V002
```

方案编号在整个专题内唯一，禁止重置或复用。机制名称保存在 manifest 的 `name` 中，目录使用 `variants/VNNN/`。禁止因优先级变化而重命名方案。

### 执行

使用可排序且不易冲突的 ID：

```text
YYYYMMDD-HHMMSS-<agent>-<task-or-role>-NN
```

示例：

```text
20260909-143012-codex-double-buffering-01
20260909-151820-claude-audit-01
20260909-160405-pi-benchmark-01
```

可能跨主机并发创建执行时，必须追加简短主机标识或随机后缀。

### 产物

使用语义稳定的名称：

```text
manifest.json
report.md
correctness.json
benchmark.json
benchmark.md
environment.json
stdout.log
build.log
final.diff
```

方案身份由目录表达，无需在每个文件名中重复编码。

## 状态机

专题：`proposed -> active`。活跃专题可以暂停/恢复、完成或中止。完成前，所有已启动方案必须有终态决策或明确取消记录。归档通过外部记录表达，并保留原终态结果。

方案：`proposed -> planned -> implementing -> testing -> auditing`。测试失败或审计无定论时，可转为 `needs_revision`，随后使用新执行继续实现、测试和审计。任何非终态都可以在记录理由后取消或拒绝。`accepted` 可通过带日期的决策转为 `superseded` 或 `final`。仅做验证的任务可说明原因后省略实现阶段。`inconclusive` 是验证结论，不是方案终态决策。

执行状态转换：

| 当前状态 | 允许的下一执行状态 |
|---|---|
| `pending` | `running`、`failed`、`cancelled` |
| `running` | `completed`、`failed`、`cancelled` |
| `completed`、`failed`、`cancelled` | 无；保留当前结果，后续执行创建新 Run |

编排者验收独立转换：`pending -> passed` 或 `pending -> needs_repair`。已提交执行的修复必须有自己的执行和验收记录，旧记录保留。归档与替代关系属于外部元数据，不能覆盖执行状态。执行者未写入终态就停止时，根据编排者的终止记录恢复工作，禁止冒充执行者补写状态。

工作树：`created -> active -> completed -> removed`，适用时记录集成或放弃。已完成的测试/审计工作树不要求合并。只有产物生成进程已停止、恢复检查通过且清理获授权后，才允许删除。

`accepted` 表示方案的精确 commit 已通过决策验收；`final` 表示它是专题选定的最终结果。缺少必需证据时，禁止用任何状态暗示成功。

## 端到端生命周期

代码修改任务由编排者按以下顺序推进：

1. 发现实际主仓库路径和现有项目布局，检查说明、活跃工作树及未提交状态。
2. 获取项目或专题协调范围的编排所有权。
3. 定义任务、角色、负责人、基准引用、分支、工作树和执行 ID。
4. 从明确 commit 创建分支和工作树。
5. 创建持久执行目录、不可变 `assignment.json` 和 `pending` manifest。
6. 添加仓库本地忽略规则，创建 `.agent-artifacts/` 链接，并验证忽略规则和分配的执行路径。
7. 冻结此次执行的协议快照，填充 `worker-start.md`，使用绝对路径启动执行者，并明确要求先读合约、再读启动引导。
8. 要求执行者在修改源码前完成启动前握手。
9. 执行者仅在分配范围内实现，并记录偏差。
10. 执行者自由探索、测试、运行基准测试和性能分析，保留临时实验，并在交接时收集持久证据。
11. 提交预期修改，针对该精确源码状态验证结论，停止产物生成进程，并提交 `manifest.json` 和 `report.md`。
12. 验收终态执行，写入 `validation.json`。
13. 需要时，从独立工作树审查或审计精确结果 commit。
14. 作出并记录接受、拒绝、替代或取消决定。
15. 接受后，通过指定集成流程合并。
16. 由汇总者更新共享汇总。
17. 验证可恢复性，然后清理可删除工作树和符合条件的分支。
18. 在不可变执行目录之外记录归档，并释放编排所有权。

任何昇腾算子专题都必须在第 2 步取得所有权之后、实现之前，建立参考资料包和方案记录。只有专题类型需要有意义的比较依据时，才建立基线。

## 并发与所有权

每个可变文件或命名空间只分配一名写入者：

| 资源 | 写入者 |
|---|---|
| 编排注册信息和租约 | 活跃编排者 |
| 执行者的 `assignment.json` | 编排者；派发后不可变 |
| 活跃执行者的 `manifest.json` 和 `report.md` | 分配的执行者 |
| 执行的 `validation.json` | 执行者终止后的编排者 |
| 工作树源码 | 分配的实现 Agent |
| 执行目录 | 分配的执行负责人 |
| 方案结果 | 结果负责人或指定基准测试 Agent |
| 方案审计 | 独立审计者 |
| 方案决策 | 专题决策负责人 |
| 专题方案索引与身份分配 | 编排者 |
| 共享汇总文件 | 唯一汇总者 |
| 集成分支 | 集成者 |

Agent 可读取其他执行和方案的产物，但禁止静默重写。通过新审计、决策、修正说明或替代执行保留来源与历史。

多个 Agent 需要同一代码基线时，即使任务不同，也必须各自分配独立工作树。只读任务建议使用固定在精确 commit 的 detached 工作树。

## 清理与保留

删除工作树前，必须核实：

- 每个结果，包括被拒绝的工作，都可通过持久 Git ref/bundle 恢复，或拥有已验证的恢复补丁及其基准、必需的未跟踪文件和二进制内容。仅记录 SHA 不等于保留代码。
- `manifest.json` 记录终态、基准 commit 和存在时的结果 commit。
- `report.md` 记录验证、风险和未完成工作。
- 必需的原始测试、基准测试和性能分析产物已持久保存在工作树之外。
- 已记录决策或取消理由。
- 不遗留未跟踪的用户文件或有价值的本地状态。
- 执行者及所有产物生成子进程均已停止，没有活跃 Agent 或进程使用该工作树。
- 已接受工作已合并，或其精确 commit 仍然可达。

随后使用 Git 的 worktree 命令删除工作树。只有检查过陈旧元数据后才能清理它。分支仅在已合并、已拒绝且证据已保存，或得到明确授权时才能删除。禁止将破坏性 reset 或强制删除作为常规清理手段。

保留规则：

- 长期保留 manifest、报告、决策、基准测试汇总和复现元数据。
- 长期保留失败与被拒绝方案的经验。
- 原始证据至少保留到审计和专题关闭完成。
- 超大 profiler trace 或日志按明确的项目保留策略处理。
- 原始文件到期删除时，必须保留校验和、元数据、汇总和删除记录。
- 归档后禁止修改历史执行内容；通过追加修正记录处理更正。
- `latest` 符号链接或索引可以指向最新执行，但禁止替代不可变历史。

## 跨 Agent 派发说明

向 Codex、Claude、Pi、Herdr 或其他 Agent 派发任务时，加入或适配以下说明：

```markdown
## 工作树与产物协议

你拥有一个执行目录；代码角色还拥有一个分配的 Git 工作树。

- 首先读取启动提示中给定绝对路径的 `assignment.json` 和 `worker-start.md`，再阅读冻结协议与必需输入，之后才能执行任务。
- 合约不可变，是任务的权威依据。
- 修改源码前必须完成启动前握手。
- 代码操作从分配的工作树根目录开始，并保持在该工作树根目录。
- 编辑前确认预期分支或 detached commit。
- 禁止修改其他 Agent 的工作树、分支、执行目录或汇总文件。
- 通过指向项目产物根目录的固定 `.agent-artifacts/` 链接发现专题并读取相关上下文；禁止重定向链接。
- 持久输出使用不可变的绝对 `artifacts.run_directory`，并显式传给子进程；提交前收集临时证据。
- 必需文件包括 `<run_directory>/manifest.json` 和 `<run_directory>/report.md`；必须完成合约中的每项输出。
- 原始证据保存在 `logs/`、`tests/`、`benchmarks/`、`profiling/`、`patches/`、`attachments/` 或 `environment/`。
- 未经明确要求，禁止将原始执行产物提交到 Git。
- 工作前记录基准 commit，提交预期修改后记录结果 commit。
- 明确报告未运行的测试或基准测试。
- 记录偏差、风险和未完成工作。
- 除非明确分配相应角色，否则禁止合并、删除分支、移除工作树或重写共享汇总。
```

昇腾算子专题任务追加：

```markdown
本次执行属于指定专题和方案下的华为昇腾算子任务。首先确认分配的昇腾硬件以及 CANN 或框架目标，再读取专题 README、参考资料、适用基线、当前 `summary/status.md`、专题方案索引和本方案的前序记录，之后再开始行动。必须保留 `hypothesis -> proposal -> plan -> implementation -> result -> audit -> decision` 记录链。原始证据保存在执行目录，结论保存在方案文档。新开发必须验证规格、正确性判定依据、昇腾集成与验收目标；优化或重构还必须将有效结果与原始基线和当前选定方案比较。禁止编造不适用的基线。未明确授予决策权时，禁止接受自己的结果。
```

不同工具的启动命令可以不同，但协议与所有权规则相同。

## 各角色执行说明

### 编排者

- 从项目容器根目录启动，禁止在那里修改业务源码。
- 分配可变身份前必须取得排他的协调所有权。
- 创建准确合约、工作树、执行、产物链接和初始 `pending` manifest。
- 准备冻结的执行级协议快照和启动文件，使用明确启动路径派发，禁止假定 Skill 会自动继承。
- 对活跃执行者的执行内容只读。
- 推进状态前验证终态证据并写入 `validation.json`。
- 重试创建新的替代执行，禁止重写执行历史。
- 按明确权限分配实现、独立审计、集成、汇总和清理职责。

### 实现执行者

- 仅在分配的工作树内编辑。
- 遵循计划，或记录偏差。
- 涉及源码修改时，产出已提交的结果。
- 禁止自行批准基准测试有效性。

### 测试或基准测试执行者

- 将任务固定到精确 commit。
- 保留完整命令、环境、原始输出和失败记录。
- 除非被重新分配为实现执行，否则禁止仅为使测试通过而修改实现。

### 审查或审计执行者

- 审查精确结果 commit，禁止以持续变化的分支顶端代替。
- 根据产物和代码核实报告中的判断。
- 分别记录正确性、方法、可复现性和可维护性问题。
- 证据不足时记录 `inconclusive`。

### 集成者

- 仅合并已接受的 commit。
- 多方案相互影响时重新执行集成级检查。
- 记录冲突解决过程和产生的合并 commit。
- 禁止将实现者的工作树用作集成工作树。

### 汇总者

- 读取 manifest 和最终报告，禁止根据目录名推断成功。
- 只有单位和环境可比时才统一指标口径。
- 作为唯一写入者更新项目或专题汇总。
- 保留指向精确方案、执行、产物和 commit 的链接。

## 恢复已有工作

加入现有项目或专题时：

1. 根据现有布局与 Git 元数据重新发现实际项目容器、主仓库、工作树和持久 `agent-artifacts/` 根目录，禁止假定固定目录名。
2. 读取仓库说明，检查活跃工作树。
3. 专题任务读取 `README.md`、`manifest.json`、参考资料、适用基线文档、`summary/status.md`、`summary/decisions.md` 和活跃方案索引。
4. 检查目标方案及其记录链中的全部前序文档。
5. 阅读相关执行 manifest 和报告，按需打开原始产物。
6. 继续前验证分支与 commit 身份。
7. 新执行创建新 Run，禁止向已归档执行追加新输出。

记录冲突时，以精确 commit 和原始证据为事实依据，标明不一致，向对应负责人询问或创建修正记录。

## 完成检查清单

所有适用检查通过前，禁止报告完成：

- [ ] Agent 在分配的工作树根目录操作。
- [ ] 项目或专题协调范围恰有一名编排者持有所有权。
- [ ] 每次派发执行均保留不可变 `assignment.json`。
- [ ] 执行者首先读取合约，并确认专题/方案/执行身份、精确输出路径、commit、链接解析结果、输入和权限。
- [ ] 工作树链接始终指向项目产物根目录；产物生成子进程使用不可变的绝对执行目录。
- [ ] 执行状态、测试/审计结论、编排者验收和方案决策相互区分。
- [ ] 并行写入者使用独立工作树和分支。
- [ ] 仓库本地 Git 元数据已忽略 `.agent-artifacts`，未修改全局 Git 配置。
- [ ] 持久产物位于可清理工作树之外。
- [ ] 分别记录执行与工作树身份。
- [ ] `manifest.json` 有效、处于最终状态，并指向精确 commit。
- [ ] `report.md` 汇总结果、验证、风险和交接。
- [ ] 编排者的 `validation.json` 记录完成验收结果。
- [ ] 原始日志、测试、基准测试、性能分析和补丁使用标准目录。
- [ ] 算子工程记录保留完整方案记录链。
- [ ] 参考资料、正确性判定依据和验收标准明确。
- [ ] 仅在适用且方法有效时，使用基线和当前选定方案进行比较。
- [ ] 需要独立审计与决策时，已分别记录。
- [ ] 共享汇总由指定汇总者更新。
- [ ] 被拒绝和被替代的工作仍可发现。
- [ ] 清理保留了全部可恢复代码和证据。

## 协议要点

牢记八项不变量：

```text
每个并发代码写入 Agent -> 一个工作树
每次执行              -> 一个 Run
每个协调范围          -> 一名活跃编排者
每个被派发执行者      -> 一份不可变合约
工作树                -> 可清理的代码环境
agent-artifacts       -> 持久证据与知识
manifest.json         -> 执行与 Git 状态的来源关联
唯一汇总者            -> 无并发写冲突的共享汇总
```

本协议用于保留可信、可复用的记录：修改了什么、如何验证、结论为何可信、哪些思路失败，以及后续 Agent 如何在已有证据上继续工作，避免重复丢失的尝试。
