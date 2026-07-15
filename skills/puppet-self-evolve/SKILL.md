---
name: puppet-self-evolve
description: "完整自进化执行技能。仅在两类场景使用：用户明确要求固化为全局 Rule/Skill/Hook、写入 puppet-vault 或晋升通用能力；或 puppet-vault-curator 提交已成熟候选。须读全文获取 E0-E6 流程、三级分层判断、替换测试三问、AskQuestion 确认、EVOLUTION_LOG 门禁与 [PUPPET_EVOLVED] 输出规范。不要用于 stop hook、普通纠正、候选计数、项目进度总结或个人长期记忆。"
---

# Puppet 自进化执行技能 (puppet-self-evolve)

## 定位

本技能负责把**已明确要固化**、或 **puppet-vault-curator 判定成熟**的候选，经过用户确认后写入私有全局 `puppet-vault` 层。

| 技能 | 职责 |
|------|------|
| `sc-inline-reflect` | 对话内轻量反思，写项目层并输出 `[SC_INLINE_REFLECT_DONE]`；有全局价值时按需调用 curator |
| `puppet-vault-curator` | 候选池管家：查重、聚合、成熟度判断并输出 `[SC_CANDIDATE_DRAFTED]`；成熟后触发本技能 |
| `puppet-self-evolve`（本技能） | 用户显式要求或 curator 成熟候选触发；AskQuestion 确认后写全局并输出 `[PUPPET_EVOLVED]` |
| `sc-promote-to-repo` | 将成熟私有规则/技能晋升发布到通用仓库 |
| `sc-memory-layered` | 用户偏好/事实层长期记忆 |

---

## 触发判定

本技能只在以下两类场景触发：

### 1. 用户显式触发

- "固化这个经验 / 做成规则 / 做成 skill / 写成 Rule"
- "升级为全局规则 / 写入 puppet-vault / 晋升到通用仓库"
- "这条要永久生效 / 以后别这样"
- "把这个 Hook/Skill/Rule 做成全局能力"

### 2. puppet-vault-curator 触发

`puppet-vault-curator` 判断候选已成熟（通过成熟度门禁）后，提交成熟候选触发本技能。

### 不再触发本技能的场景

| 场景 | 处理组件 |
|------|---------|
| 对话中用户纠正 / 踩坑 / 成功路径 | `sc-inline-reflect` |
| 全局候选记录与触发次数更新 | `puppet-vault-curator` |
| stop hook 会话结束 | `memory_stop_review.py` 只做标记兜底 |
| 项目进度/交接总结 | `sc-context-reset` |
| 个人偏好/长期记忆 | `sc-memory-layered` |

---

## 架构边界

```text
当前工作区（项目专属）
  <workspace>/
    .agents/rules/*.mdc        # 新增默认
    .agents/skills/*/SKILL.md  # 新增默认
    .agents/hooks/**           # 新增默认
    .agents/scripts/**         # 新增默认
    .cursor/rules/*.mdc        # 历史兼容读取
    .cursor/skills/*/SKILL.md  # 历史兼容读取
    project_context.md

本机私有（不进仓库）
  <vault_root>/
    rules/*.mdc
    skills/*/SKILL.md
    hooks/**
    scripts/**
    EVOLUTION_LOG.md
    memory/session_learnings.md

通用发布（仅用户显式要求或后续晋升）
  publish_dir/plugins/
```

红线：

1. 禁止将 `puppet-vault/` 目录整体放入 `publish_dir/plugins/`。
2. 禁止将管理工具（`puppet-self-evolve`、`sc-promote-to-repo` 等）写入本机 `puppet-vault/skills/`。
3. 禁止把项目专属经验默认写入 `puppet-vault/`。
4. 直接发布到 `publish_dir/plugins/**` 仅限用户显式要求，且必须做发布层清洗。

---

## E0-E6 执行流程

### Step E0：初始化检查

```cmd
"<skill_root>/scripts/check_init.cmd" --workspace "<workspace>"
"<skill_root>/scripts/check_init.cmd"
```

WSL/Linux/macOS：

```sh
sh "<skill_root>/scripts/check_init.sh" --workspace "<workspace>"
sh "<skill_root>/scripts/check_init.sh"
```

- Windows 默认使用 `check_init.cmd`，WSL/Linux/macOS 使用 `check_init.sh`，均优先解析 Python3。
- 仅诊断/兜底时直调 `check_init.py`。
- `<skill_root>` 表示当前技能自身运行态根目录。Cursor/Codex 可通过入口链接到 `<vault_root>/skills/puppet-self-evolve`，但唯一正本仍是 `<vault_root>`。
- 若 `<skill_root>` 是符号链接目录，Linux/WSL/macOS 检查脚本时使用 `find -L` 或 `readlink`，不要用普通 `find` 误判脚本缺失。
- 执行前必须把 `<skill_root>` 展开为当前技能自身的运行态根目录，禁止按当前工作区猜测脚本位置。

脚本输出用于判断：

- `puppet-vault` 是否存在
- 当前项目 `.agents/rules/`、`.agents/skills/`、历史 `.cursor/rules/`、历史 `.cursor/skills/`、`project_context.md` 是否已有相关条目
- 是否应新建或迭代已有内容

### Step E1：提取固化内容

用一句话描述触发点：

- 被纠正了什么？（行为/口径/路径/工具选择）
- 找到了什么成功路径？（工作流/解法）
- 有什么踩坑教训？

输出摘要：

```text
[触发类型] | [范围:局部/项目/全局/待判断] -> [一句话描述]
```

### Step E2：范围和类型判断

#### 2.1 三层范围

| 范围 | 判断 | 写入 |
|------|------|------|
| 局部 | 仅当次任务/一次性结论有效 | 任务 notes 或临时说明，不写规则/技能 |
| 项目 | 当前工作区内反复有效，离开项目失效 | 项目 `.agents/`、`project_context.md`、项目约定目录；读取兼容历史 `.cursor/` |
| 全局 | 跨项目、跨技术栈或跨场景复用 | `puppet-vault/` |

#### 2.2 替换测试三问

全部通过才允许全局：

| 问题 | 若答否 |
|------|--------|
| Q1. 换成非本技术栈/引擎的项目还适用吗？ | 项目/技术栈专属 |
| Q2. 换成完全不同业务领域还适用吗？ | 业务专属 |
| Q3. 在其他人的机器上也有意义吗？ | 本机专属 |

#### 2.3 反例排除

以下情况不得写全局：

- 代码 Bug 被修了，但 AI 全程判断正确
- 一次性数据查询结论
- 临时调试路径/一次性命令参数
- 需要大量背景才能理解
- 含项目特定词且去项目化后失去操作性

#### 2.4 新建 vs 迭代

| 条件 | 动作 |
|------|------|
| 无现有内容 / 描述完全不重叠 | 新建 |
| 有相似 description（触发场景一致或重叠 > 50%） | 迭代，`verified_count +1` |
| 相关但不完全重叠 | 新建 + 引用已有 |

输出分类结论：

```text
分类结论：类型=<Rule/Skill/Hook/Script/Context> | 范围=<局部/项目/全局> | 写入目标=<精确路径> | 不选另一层原因=<一句话>
```

### Step E3：AskQuestion 确认

全局写入前必须确认。用户只确认是否写入，不承担分类判定。

```text
标题：全局规则确认
问题：以下经验已达到全局写入标准：
      「<去项目化后一行规则>」
      建议写入：<目标路径>
选项：
  1. 写入全局规则/技能/Hook
  2. 暂不写入，保留候选池
  3. 这条不合适，标记 rejected
```

各选项后续处理：

| 选项 | 动作 |
|------|------|
| 1. 写入 | 执行 E4-E6，写文件 + 更新 `candidate_pool.md` 中该候选 `**成熟度**：mature` + 追加 EVOLUTION_LOG |
| 2. 暂不写入 | 仅记录跳过，`candidate_pool.md` 候选条目保持不变，下次节流通过仍会提醒 |
| 3. 标记 rejected | 将 `candidate_pool.md` 中该候选 `**成熟度**` 改为 `rejected`，不再递增触发次数，不再触发全局进化 |

### Step E4：写入文件

#### Rule 模板

```markdown
---
description: "<触发场景一句话>。须读全文获取<主题词>。"
alwaysApply: true
---

# <标题>

## 触发场景
<什么协作问题导致这条规则>

## 规则内容
<具体约束>
```

#### Skill 模板

```markdown
---
name: sc-<name>
description: "<触发场景 + 主题摘要。须读全文获取执行流程。>"
---

# <标题>

## 触发条件
## 执行流程
## 禁止行为
```

#### Hook / Script

- 全局 Hook：`<vault_root>/hooks/`
- 全局 Script：`<vault_root>/scripts/`
- 项目 Hook/Script：`<workspace>/.agents/hooks/` 或 `<workspace>/.agents/scripts/`

### Step E5：追加 EVOLUTION_LOG

凡写入 Rule/Skill/Hook/Script/Context/EvoNotes，必须追加：

```markdown
| YYYY-MM-DD | Rule/Skill/Hook/Script/EvoNotes | 文件名 | 触发原因 | 1 | 待评估 |
```

### Step E6：反馈和标记

必须输出：

```text
已完成 Puppet 全局自进化：[新建/迭代] [类型] -> [文件名]
摘要：[一句话]
路径：[完整绝对路径]
已追加 EVOLUTION_LOG。
[PUPPET_EVOLVED]
```

`[PUPPET_EVOLVED]` 只能由本技能在全局写入完成后输出，供 stop hook 判断全链路已完成。

---

## 直接发布例外

若用户明确说“直接固化到通用仓库 / 不需要先到私有目录再晋升”，且经验已具跨项目通用性，可直接写 `publish_dir/plugins/**`。

必须补做：

1. 目标插件路由
2. 二次判断：经验是否通用，正文是否适合发布
3. 发布层清洗：去掉私有流程名、验证态措辞、来源痕迹
4. 运行态同步与提交

---

## Trigger Examples

- “把这个经验固化成全局规则”
- “这个流程可以跨项目复用，做成 skill”
- “curator 提示这个候选已经成熟，帮我确认写入”
- “把这个 Hook 做成全局能力”
- “晋升到通用仓库”

---

## Constraints

1. 不替代 `sc-inline-reflect`：对话内轻量纠正、踩坑、成功路径由 inline 处理。
2. 不替代 `puppet-vault-curator`：候选池查重、触发次数、成熟判断由 curator 处理。
3. 不替代 `sc-memory-layered`：用户偏好/长期记忆路由到 memory。
4. 全局写入必须 AskQuestion 确认。
5. 写入完成必须输出 `[PUPPET_EVOLVED]`。
6. 直接发布必须做发布层清洗。
7. EVOLUTION_LOG 必须与写入同轮完成。
8. 新建 Rule/Skill 前必须先判断是否应迭代已有内容。
9. 用户只确认是否写入全局，不承担 Rule/Skill/Hook 分类判断。
