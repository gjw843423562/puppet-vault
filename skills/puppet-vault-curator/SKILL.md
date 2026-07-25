---
name: puppet-vault-curator
description: "Puppet 全局进化候选池管家。触发：puppet-inline-reflect 提交全局候选、用户说整理候选/看看哪些可以晋升/成熟化规则、或候选池积累较多时。须读全文获取 candidate_pool 脚本用法、查重聚合、成熟度门禁、draft_only 边界与 [PUPPET_CANDIDATE_DRAFTED] 输出规范。本技能不直接写全局 rules/skills。"
---

# Puppet 候选池管家

## 定位

自进化三段链路的第二段：管理全局候选池，负责查重、聚合、触发次数、成熟度判断。全局写入仍由 `puppet-self-evolve` 在用户确认后执行。

## 候选池位置

| 文件 | 说明 |
|------|------|
| `<vault_root>/memory/candidate_pool.jsonl` | 每行一条候选，不进入 Git |
| `<vault_root>/EVOLUTION_LOG.md` | 全局写入与候选成熟记录，可同步 |

`<vault_root>` 表示 puppet-vault 唯一正本目录。

## 脚本入口

| 平台 | 命令 |
|------|------|
| Windows | `<skill_root>/scripts/candidate_pool.cmd <action>` |
| WSL/Linux/macOS | `sh <skill_root>/scripts/candidate_pool.sh <action>` |

`<skill_root>` 表示当前技能自身运行态目录，执行前必须展开。

## 候选结构

```json
{
  "id": "YYYY-MM-DD-hash8",
  "name": "候选名",
  "type": "GlobalCandidate",
  "trigger_count": 1,
  "maturity": "candidate",
  "rule": "去项目化后的规则文本",
  "evidence": [{"summary": "证据摘要"}],
  "created_at": "YYYY-MM-DD",
  "updated_at": "YYYY-MM-DD"
}
```

## Instructions

### 1. 查重

先执行：

```cmd
candidate_pool.cmd check "候选名"
```

若已存在且非 rejected，更新触发次数和证据；若不存在，新建候选。

### 2. 新增或更新

```cmd
candidate_pool.cmd add --name "候选名" --rule "规则文本" --evidence "证据摘要"
candidate_pool.cmd update <id> --trigger-count +1 --add-evidence "证据摘要"
```

### 3. 成熟度判断

全部满足才可标记 mature：

| 门禁 | 要求 |
|------|------|
| 替换测试 | 技术栈、业务领域、机器环境三问全部通过 |
| 独立证据 | 至少 2 次独立出现 |
| 去项目化 | 无具体项目路径、业务名、人名、账号 |
| 约束对象 | 约束 AI 行为或通用工程行为 |
| 反例排除 | 不属于一次性结论、隐私、项目私货 |

成熟后执行：

```cmd
candidate_pool.cmd mature <id>
```

再由用户显式触发或确认 `puppet-self-evolve`。

### 4. 输出标记

候选池成功新增或更新后输出：

```text
[PUPPET_CANDIDATE_DRAFTED]
```

## Constraints

- 不弹 AskQuestion。
- 不直接写 `rules/`、`skills/`、`hooks/` 全局层。
- 不输出 `[PUPPET_EVOLVED]`。
- rejected 候选不再递增触发次数。
- 有脚本变更时，提交前必须运行 `candidate_pool.py --help`。
