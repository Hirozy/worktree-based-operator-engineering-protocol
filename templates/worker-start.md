# 执行者启动引导

你是分配给本次华为昇腾算子任务的执行者（Worker）。本启动引导是不可变合约的展示，不是第二份合约。未经明确授权，禁止自行成为编排者（Coordinator）或派发其他执行者。

## 首先读取

执行任务命令或修改文件前（允许只读启动检查）：

1. 首先读取 `<assignment-absolute-path>`，检查合约是否指向本启动引导，并确认你的角色。
2. 读取 `<protocol-absolute-path>` 及适用的仓库和 Agent 说明。
3. 读取合约 `inputs` 中的全部文件。本次任务的必读上下文如下：

<required-reading-list-with-absolute-paths>

编排者必须在启动提示词中写明“首先读取合约”，并给出合约和本启动引导的绝对路径。禁止假定 Agent 会自动发现本文件或本地安装的 Skill。

## 准确目录与链接映射

```text
working directory: <working-directory-absolute-path>
repository:        <repository-absolute-path>
worktree:          <worktree-absolute-path-or-not-applicable>
artifact root:     <artifact-root-absolute-path>
campaign:          <campaign-id-and-absolute-directory-or-not-applicable>
variant:           <variant-id-and-absolute-directory-or-not-applicable>
run:               <run-id-and-absolute-directory>
context link:      <absolute-link-path-to-artifact-root-or-not-applicable>
```

存在上下文链接时，其目标始终为项目产物根目录。禁止指向专题、方案或执行目录，也禁止随任务切换而改变。合约声明 `entrypoint: null` 时，直接使用绝对路径，禁止自行创建替代链接。

目录名必须保持协议中的英文拼写、单复数与大小写。专题下使用 `variants/V001/` 这类目录，禁止改成中文名称、`variant/`、小写 `v001/` 或带描述后缀的目录。方案名保存在 `name`，不改变目录 ID。

必须根据合约核对以下关系：

| 字段或位置 | 路径基准 |
|---|---|
| `artifacts.run_path` | 相对于 `artifacts.root_directory`；方案执行为 `campaigns/.../variants/VNNN/runs/...` |
| `artifacts.run_directory` | `artifacts.root_directory` 与 `artifacts.run_path` 拼接得到的绝对路径 |
| `startup.assignment_file` | 执行目录内的 `assignment.json` |
| `startup.bootstrap_file` | 执行目录内的 `worker-start.md` |
| `startup.protocol_file` | 执行目录内的 `protocol/SKILL.md` |
| `required_outputs` | 全部相对于本次执行目录；禁止相对于 `.agent-artifacts` 根目录直接写入 |
| `inputs`、`reviewed_runs[].manifest_file` | 合约中给出的绝对路径 |

专题公共资料使用 `reference/`、`baseline/`、`summary/`；执行证据使用 `logs/`、`tests/`、`benchmarks/`、`patches/`、`profiling/`、`attachments/`、`environment/`，按需创建。专题级执行位于专题的 `runs/`，独立任务位于项目产物根目录的 `runs/`；只有属于具体方案的执行才放入该方案的 `runs/`。

## 层级含义与所有权

- 专题（Campaign）是共享的算子目标，以及相关参考资料、基线和验收标准。
- 方案（Variant，`V001`、`V002` 等）是一个具体假设或实现方式。ID 在整个专题内唯一；方案不表示执行者或某次执行。
- 执行（Run）是分配角色针对精确源码 commit 开展的一次活动。实现、测试、基准测试和审计分别记录为独立执行。重试必须分配新执行 ID。
- 按需读取完整专题索引，以及相关并行方案和历史记录。可读目录不代表获得写入所有权。
- 允许在分配的工作树或获准临时空间内创建临时脚本、构建文件、性能分析数据和中间输出；交接前必须将持久证据收集到分配的执行目录。

## 必需持久输出

<required-output-list-with-absolute-destinations>

必须将不可变的绝对执行目录显式传给子进程。禁止根据 cwd、latest 链接、目录扫描或其他执行者的当前任务选择输出位置。额外写入共享文档时，合约必须明确授予准确文件的所有权。

## 启动前确认

核实实际工作目录、Git 工作树及共享仓库、分支/基准或目标 commit、产物根目录与链接、执行目录、输入可读性和目标位置可写性。将实际解析值和合约 ID 写入 `manifest.preflight`，包括每个必需输出的目标路径。仅处理产物的角色必须注明不适用的代码检出检查及理由。

向编排者回报此映射，启动前检查通过后才继续。路径、链接、输入、所有权或 commit 不一致时，必须报告；禁止猜测替代路径或编辑源码。

## 交接

停止产物生成子进程，收集必需证据，提交 manifest/报告，记录精确 commit 并明确未执行的验收项。执行完成、测试/审计结论和方案接受是不同状态。接受、合并或清理之前必须由编排者验收；最终聊天回复不能独立关闭任务。

禁止重写合约、本启动引导或冻结协议。已提交执行必须保留，后续执行或修复使用新分配的执行记录。
