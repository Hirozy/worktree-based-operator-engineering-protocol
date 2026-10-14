<!-- BEGIN operator-project:<primary-repository-absolute-path> -->
# 昇腾算子项目目录说明

本段仅适用于主仓库 <primary-repository-absolute-path> 及其 Git 注册工作树，
不适用于同一父目录下的其他项目。使用前以 Git 元数据核实路径。

| 位置 | 用途 |
|---|---|
| <primary-repository-absolute-path> | 主仓库，保留实际目录名；默认协调、汇总和组织集成 |
| <worktrees-root-absolute-path> | 任务工作树容器，每个实际 worktree 隔离代码修改 |
| <artifact-root-absolute-path> | 工作树之外的持久 Campaign、Variant、Run 与证据 |
| <project-container-absolute-path>/AGENTS.md | 本项目布局和角色入口说明 |

## 当前位置决定默认职责

- 在本项目注册的任务 worktree 内（包括子目录）：作为 Worker，先回到工作树根目录。
- 在本项目主仓库或已确认的项目容器：默认 Coordinator。
- 检查 git worktree list --porcelain；不要按目录名、分支名或 .git 文件外观猜测。
- 用户明确指定角色时尊重指定；角色判断本身不授予修改、提交、合并或删除权限。
- 位置或项目身份不确定时先询问，禁止接管其他项目。

## Worker 启动

由用户粘贴 Coordinator 提供的启动提示，再读其中明确的 SKILL.md 和 task.md，
核实任务和产物目录；本说明不代替手动启动提示，不修改项目原有指令文件。
已确认创建 Campaign 时，工作树的 .agent-artifacts 指向该 Campaign；
其中 README.md 解释工作树用途，variants/<variant>/runs/<run>/ 保存执行记录。
没有明确 task 时请求分配；不自行创建 Campaign、Run 或另一个 worktree，
不根据“最新”记录猜测任务。不得修改共享 campaign.json 或其他 Worker 的产物。
<!-- END operator-project:<primary-repository-absolute-path> -->
