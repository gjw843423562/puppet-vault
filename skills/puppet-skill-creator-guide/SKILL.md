---
name: puppet-skill-creator-guide
description: "Puppet 私有 Skill 创建、优化与质量验收技能。触发：创建/优化/审查 puppet-vault 技能、改 SKILL.md、改 description/触发词、拆 references、添加 scripts、把个人流程固化成技能时。须读全文获取中文 Skill 写法、渐进披露、质量六维、脚本自测、跨 Agent 路径与交付清单。优化现有 Skill 前先走 puppet-rule-skill-decider。"
---

# Puppet Skill 创建与优化指南

## 定位

本技能用于把个人高频工作流沉淀成 puppet-vault Skill，并保持轻量、可触发、可执行、可维护。

## 前置门禁

1. 优化现有 Skill 前，先执行 `puppet-rule-skill-decider`。
2. 新建 Skill 前，必须给出“复用现有 / 合并增量 / 独立新文件”结论。
3. 只在用户明确要写入 puppet-vault，或候选已成熟时落盘。

## 标准结构

```text
skills/<skill-name>/
  SKILL.md
  references/   # 长规范、分场景说明，按需读取
  scripts/      # 确定性脚本；Windows/通用入口成对
  assets/       # 模板、静态资源，仅在真实需要时创建
```

`skill-name` 使用小写连字符，必须与 frontmatter `name` 一致。

## SKILL.md 写法

1. `description` 只写能力、触发场景、负向边界；不要塞长路径、命令大全或正文禁令。
2. 正文使用中文，优先包含：定位、快速参考、Instructions、Trigger Examples、Constraints。
3. 多阶段工作流必须写明 checklist、门禁和结束条件。
4. 长表、领域规范和案例迁入 `references/`，正文保留“何时读哪份”的分流表。

## 质量六维

| 维度 | 最低要求 |
|------|----------|
| 可发现性 | description 覆盖用户自然说法 |
| 可执行性 | 步骤可照做，关键门禁可判断 |
| 可维护性 | 主文不过度膨胀，资料分层 |
| 安全与合规 | 写入、删除、提交、敏感信息有红线 |
| 通用性与分层 | 不混入项目私货和一次性日志 |
| 可演进性 | 有验证清单，脚本有自测入口 |

## 脚本规则

1. 复杂逻辑写 Python，`.cmd` / `.sh` 只负责定位 `skill_root`、解析 Python、透传参数。
2. Windows 提供 `scripts/<name>.cmd`，通用入口提供 `scripts/<name>.sh`。
3. 每个改动的 `.py` 至少支持 `--help` 并零退出；若仓库有烟测，提交前必须运行。
4. `<skill_root>` 表示当前技能自身运行态目录，不能等同当前工作区。

## 体量门禁

| 指标 | 黄区 | 红区 |
|------|------|------|
| 行数 | >400 | >650 |
| UTF-8 字符 | >14000 | >22000 |

触黄区时规划拆 `references/`；触红区时先拆层再追加正文。

## Trigger Examples

- "帮我创建一个 puppet skill。"
- "这个技能触发词不够，优化一下。"
- "把这个流程固化成个人技能。"
- "检查这个 SKILL.md 是否合格。"

## Constraints

- 不在技能根目录创建无关 README、CHANGELOG 或说明噪音。
- 不把公司业务 SOP 原样搬进 puppet；必须先做去项目化与私有层清洗。
- 不把项目专属路径、日志、业务字段写入全局 Skill。
- 有脚本变更时，未跑最低自测不得提交。
