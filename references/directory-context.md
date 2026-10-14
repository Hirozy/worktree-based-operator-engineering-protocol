# 目录识别与角色

这是启动前的只读判断，不创建工作树、Campaign 或任务。
只在本 Skill 适用的昇腾算子任务内使用，不覆盖用户明确角色或更高优先级说明。

## 判断步骤

1. 解析当前目录的真实路径，读取适用的项目说明；不要仅凭目录名猜测。
2. 当前目录处于 Git checkout 时，执行：

```bash
git rev-parse --show-toplevel
git rev-parse --path-format=absolute --git-dir
git rev-parse --path-format=absolute --git-common-dir
git rev-parse --show-superproject-working-tree
git worktree list --porcelain
```

3. 将 checkout 根目录与清单中的路径按真实路径比对，识别主工作树或已注册的 linked worktree。
   git-dir 与 common-dir 不同只是线索，不能单独作为判断；子模块也可能不同。
   在子模块内时沿 superproject 回到外层 checkout，再按其注册身份判断所属任务工作树。
   子模块中的任务修改仍遵守项目约束，不将子模块自身误认为独立 Worker 工作树。
4. 匹配 linked worktree 时，无论是 detached HEAD、分支模式、宿主管理路径还是其子目录，
   自动选择 Worker，并报告识别出的工作树根目录。路径不符合约定则报告布局问题，
   但仍不转为 Coordinator，也不擅自重建或移动工作树。
5. 匹配主工作树时，默认 Coordinator。当前目录不是 Git checkout 时，
   使用用户路径或项目容器 AGENTS.md 的明确映射定位目标仓库，再用 Git 清单交叉核实。
   不将“不是 Git 仓库”的任意目录当成项目容器；多个候选、裸仓库或映射冲突时先询问。
   位于 artifact 或 worktrees 容器但不在具体 checkout 内时，不能直接认领某个 Worker 任务。

## Worker 的上下文入口

- 默认不执行 Coordinator 的创建后询问、分配身份、维护共享索引或新建工作树流程。
- 用户手动注入启动提示后，Worker 读取指定 Skill 和项目原有说明，核实当前工作树。
- 可只读查看已存在的 .agent-artifacts/README.md，理解大方向，然后报告就绪并等待用户具体 prompt。
  Campaign 上下文不等于执行授权；启动不要求 task.md、Variant 或 Run。
- 收到具体任务后再核实源码、输入及 Run 分配，记录 task；缺少执行分配时向用户说明，
  不选“最新”Run，不扫描后猜测一个可执行任务，不自动创建 Campaign。
- 链接缺失或指向旧布局时报告；不能自行创建、覆盖或重定向。

## 上层目录说明

上层说明是可选的布局文档，不是 Worker 的启动注入方式。
仅用户明确要求时，Coordinator 在已确认的 project-container/AGENTS.md 中使用 project-context 模板。
替换真实主仓库名称、绝对路径与工作树根目录；不要留下占位符。
若文件不存在，确认父目录安全且有写权限后创建；存在则读取并保留原内容，
只追加或更新明确标记为本项目的说明块，冲突时询问，不重写无关指令。
项目容器如果同时包含无关仓库（如共享 Projects 目录），先确认说明文件位置与范围，
不得自动添加对整个父目录生效的全局角色要求。
说明必须限定在识别出的仓库及其注册 worktree，不能只凭“位于子目录”选择 Worker。
真实 Git 状态与文档不一致时报告，不把旧文档当成创建或接管工作区的授权。
这份说明由 Coordinator 写一次并按布局变化维护，不为每个 Run 复制。
Worker 启动始终由 Coordinator 输出准确目录及已填充的 worker-prompt，用户手动粘贴。
不修改工作树内原有 AGENTS.md 或其他项目指令文件；不保证空白会话自动发现 Skill。
