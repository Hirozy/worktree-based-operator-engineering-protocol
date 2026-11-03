# 实验管理

适用于轻量流程的状态维护与迭代实验，不引入额外角色或强制文档。

## 身份与目录

Campaign 是持续工程目标；Variant 是具体假设或实现方式；
Run 是一次执行。目录必须为 `variants/<variant-id>/runs/<run-id>/`。
同一 Variant 可多次执行；Run 固定属于一个 Variant，不能移动或改绑。
Variant 和 Run 的 ID 在 Campaign 内唯一；并行创建时可加 Worker 标识与随机后缀，目录已存在则换 ID，不覆盖。
方案实质改变时新建 Variant 并记录 parent_variant；细化实现可在原方案继续。
源码起点必须明确；来源方案与性能比较对象不是同一个概念。

## 索引

campaign.json 使用 lightweight-1 版本。
顶层包含 campaign_id、objective、status、decisions、variants、runs。
模板初始数组为空；以下是数组元素的字段约定，而非必须预生成的对象。

- Variant：id、name、parent_variant（可为 null）、status、selected_commit（可为 null）。
- Run：id、variant_id、task_type、worker、worktree、base_commit、
  target_commit（无固定审查目标时为 null）、status、result_path、outcome、note。
- Campaign decisions：每条含 at、variant_id、run_ids、conclusion、reason、commit（可为 null）。
  variant_id 标识决策对象；run_ids 可引用不同方案的执行以支持比较。

result_path 相对 Campaign，必须为 variants/<variant_id>/runs/<id>/result.md。
Run 状态来自 result.md；汇总时核对实际方案和 Run 文件，补录新记录，不仅依赖旧索引。
worktree 使用真实绝对路径；仅产物分析可为 null。
outcome 是 Coordinator 根据证据记录的 passed、failed、inconclusive 或 null，
不从执行状态推导；pending 时为 null，结束但未核验时仍可为 null。
result_path 是预期位置，不表示文件已存在。失败 Run 可没有 result，由 note 解释。
同一个 Run 仅存一条完整记录，decisions 的 run_ids 只引用，不复制 Run 状态。
所有方案和执行引用必须存在；决策中的 commit 必须与支持该结论的证据对应。
新增 Run 前检查身份唯一、目录归属与源码起点；决策必须引用实际 Run。
不要重新登记或改绑历史 Run；需要重新测量时创建新 Run。
比较可在 reason 中引用旧证据及其环境限制。

## 最小状态

| 对象 | 状态 |
|---|---|
| Campaign | active / paused / completed / cancelled |
| Variant | exploring / accepted / rejected / superseded |
| Run | pending / running / completed / failed / cancelled |

Run：pending 可转 running、failed 或 cancelled；running 可转任一终态，由 Worker 更新 result.md 的状态字段。
Run 终态不可重开；测试失败但执行流程正常结束可以 completed，outcome 为 failed。
没有证据时 outcome 不得为 passed。失败、中断原因及尚存进程必须如实记录。
Variant 的 accepted 绑定 selected_commit 与明确证据。新 commit 不继承旧验证；
重新探索时保留历史决策，将当前状态设 exploring，selected_commit 清空。
被拒方案在后续重试可恢复 exploring，但保留原拒绝决定。
superseded 的原因与替代方案记入决策，旧证据不能删除。
结束 Campaign 前协调停止新执行，核实实际 Run 均结束并汇总索引、记录最终决策，不能仅凭旧索引判断。
暂停不是终止进程；仍运行的 Run 必须明确记录，不能清理其工作树。

## 写入与恢复

Coordinator 是唯一索引写入者，用临时文件完成 JSON 解析检查后原子替换索引。
不增加锁服务或状态数据库；若发现另一个 Coordinator，先协调唯一写入者再继续。
Worker 可按具体任务创建方案与 Run，维护自己创建的 proposal 和 Run；已有方案说明保持唯一写入者。
Campaign decisions 追加记录，不覆盖旧决策；README 只概述当前结论并链接证据。
恢复时读取索引、目标方案与相关结果，核对 Git 和进程实际情况；
不能根据旧 running 状态判定仍存活，也不能据文件存在就宣称成功。
崩溃后确认原写入者和进程停止，在 result 追加 failed、原因与记录者，再同步索引；不改写已有终态或验证事实。
清理前核对代码可恢复、证据存在及生产进程已停止，不仅检查 Git 工作区干净。

## 文档与例外

proposal.md 用一份文档记录假设、计划、实现变化及有用发现，不再拆七份。
决策记录在索引，原始证据在 Run，避免重复抄写。
baseline 仅在有实际比较对象时创建；reference、对比表和最终报告按内容需要增加。
普通查看与问答不建 Run；需持久保存的专题准备与汇总结论由 Coordinator 写入已有 README，不制造“汇总方案”或同级 runs 目录。
已有实验记录不删除或自动迁移；发现不匹配的索引格式或布局时报告，
由用户选择显式迁移或新建专题并引用已有证据，禁止猜测和重写历史状态。
