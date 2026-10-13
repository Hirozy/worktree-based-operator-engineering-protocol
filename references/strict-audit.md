# 可选严格模式与历史兼容

默认使用轻量流程。只有用户明确要求旧版结构化合同、冻结协议与验收门禁，
或继续已有 v2 执行时，才读取 [legacy-v2.md](legacy-v2.md)。

legacy-v2.md 是本次精简前的原始协议，保留其旧目录、角色、schema 和状态语义。
旧版合同与轻量索引是不同接口；不得用 v2 校验器校验 campaign.json。
旧字段中的 implementation/test/audit 等仍是兼容接口值，不扩充轻量流程的两类职责。
严格执行必须明确告知其额外文件成本；不因为进行测试或独立审查就自动启用。

本仓库根目录下原有 templates/assignment.json、run-manifest.json、validation.json、
worker-start.md、schemas/ 与 scripts/validate_contract.py 原样保留。
旧协议提及这些路径时均相对于 Skill 包根目录，而非 references/。
若按旧协议创建冻结快照，使用 legacy-v2.md 内容作为快照的 SKILL.md，
同时复制匹配的旧模板、schemas 和 scripts；不能将轻量入口当作旧协议快照。
历史 Run 优先使用其自己的冻结协议，不受已安装 Skill 更新影响。

继续使用旧版校验命令（<package> 为 Skill 包根或匹配的旧协议快照）：

```bash
uv run --no-project --with 'jsonschema[format]==4.26.0' python <package>/scripts/validate_contract.py <assignment.json> --check-files
uv run --no-project --with 'jsonschema[format]==4.26.0' python <package>/scripts/validate_contract.py <assignment.json> --manifest <manifest.json> --check-files
```

这些校验只处理结构和证据关联，不证明算子正确或性能有效。
