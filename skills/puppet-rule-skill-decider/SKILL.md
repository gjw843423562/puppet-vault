---
name: puppet-rule-skill-decider
description: "Puppet 私有库 Rule/Skill/Hook/Script/项目文档归属判定技能。触发：用户问规则还是技能、准备新增或优化 puppet-vault 能力、迁移 sc 能力到 puppet、拆 references、改 description/触发词、或提交前需要判断技能质量时。须读全文获取资产盘点、三选一结论、质量六维、体量预警与落地路径模板。"
---

# Puppet Rule / Skill 决策技能

## 定位

在向 puppet-vault 写入新能力前，先判断内容归属，避免把流程塞进 Rule、把红线藏进 Skill，或把项目经验误升为全局规则。

## 快速判定

| 内容类型 | 推荐位置 |
|----------|----------|
| 每轮都应自动遵守的底线、红线、触发门禁 | `rules/*.mdc` |
| 可复用的多步工作流、专业方法、工具使用流程 | `skills/<name>/SKILL.md` |
| 确定性脚本、校验器、同步器、转换器 | `skills/<name>/scripts/` 或 `scripts/` |
| 当前项目才成立的路径、口径、架构决策 | 项目 `project_context.md` 或 `.agents/` |
| 候选但未成熟的全局经验 | `puppet-vault-curator` 候选池 |

## Instructions

### 1. 资产盘点

1. 检索 `<vault_root>/rules`、`<vault_root>/skills`、`<vault_root>/references`。
2. 若当前项目存在 `.agents/` 或历史 `.cursor/`，只读取与本次主题相关的文件。
3. 输出“复用现有 / 合并增量 / 独立新文件”三选一结论。

### 2. 分层判断

对待写内容执行替换测试：

| 问题 | 否定时的去向 |
|------|--------------|
| 换技术栈仍适用吗？ | 技术栈专属规则或 Skill |
| 换业务领域仍适用吗？ | 项目文档或专用 Skill |
| 换机器或 Agent 仍适用吗？ | 本机配置或项目上下文 |

全部通过才考虑 puppet 全局层。

### 3. Skill 质量六维

| 维度 | 首版检查点 |
|------|------------|
| 可发现性 | description 是否有触发词和负向边界 |
| 可执行性 | 是否有编号步骤、门禁、输出契约 |
| 可维护性 | SKILL.md 是否过长，是否需要 references |
| 安全与合规 | 是否有写入、删除、提交、敏感信息红线 |
| 通用性与分层 | 是否混入项目路径、日志、一次性结论 |
| 可演进性 | 是否有验证清单、脚本自测、迭代入口 |

### 4. 体量预警

- `SKILL.md` 超过 400 行或 14000 UTF-8 字符：规划拆入 `references/`。
- 超过 650 行或 22000 UTF-8 字符：禁止继续往正文堆大段，先拆层。

## 输出模板

```markdown
## 资产盘点
- 技能库位置：
- 已检索范围：

## 三选一结论
- 结论：复用现有 / 合并增量 / 独立新文件
- 理由：

## 落地路径
- 类型：Rule / Skill / Hook / Script / Context
- 目标路径：
- 渐进披露：
- 质量六维：
- 同步/验证：
```

## Trigger Examples

- "这条经验该做成规则还是技能？"
- "把 sc 的这个能力迁到 puppet，先判断怎么放。"
- "优化一下 puppet 里某个 skill 的 description。"
- "新增技能前先盘点有没有可复用的。"

## Constraints

- 新建前必须先盘点已有资产。
- 结论必须唯一，不能同时建议多个默认落点。
- 涉及 Skill 创建或大改时，后续进入 `puppet-skill-creator-guide`。
- 涉及全局候选成熟化时，后续进入 `puppet-vault-curator` 或 `puppet-self-evolve`。
