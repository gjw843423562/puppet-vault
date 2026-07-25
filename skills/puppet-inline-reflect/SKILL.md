---
name: puppet-inline-reflect
description: "Puppet 对话内轻量反思技能。触发：用户纠正 AI 的路径/工具/口径/行为、连续失败后找到正确做法、复杂多步任务收尾、或用户说记一下/这个方法好/本项目以后按这样做。须读全文获取项目层写入、反例排除、全局候选提交与 [PUPPET_INLINE_REFLECT_DONE] 标记规范。不要用于个人长期记忆或普通项目进度总结。"
---

# Puppet 对话内轻量反思

## 定位

自进化三段链路的第一段：把当前对话中出现的纠正、踩坑、成功路径先写到项目层；若通过全局替换测试，再提交给 `puppet-vault-curator` 做候选聚合。

| 组件 | 职责 |
|------|------|
| `puppet-inline-reflect` | 即时记录项目层经验 |
| `puppet-vault-curator` | 管理全局候选池 |
| `puppet-self-evolve` | 用户确认后写入 puppet 全局层 |

## 触发条件

命中任一条件时，在完成当前主任务后顺带执行：

1. 用户纠正 AI 的路径、工具、口径或行为。
2. 连续失败 2 次以上后找到正确路径。
3. 复杂任务收尾，且本轮有可复用踩坑。
4. 用户说“记一下”“这个方法好”“本项目以后按这样做”。

## 反例排除

以下内容不记录：

- 一次性数据结论、临时路径、临时调试命令。
- 代码 Bug 被修复，但没有形成 AI 行为约束。
- 需要大量项目背景才能理解的细节。
- 涉及账号、密钥、token 或隐私。
- 个人长期偏好，改走记忆层。
- 阶段进度、待办和交接总结，改走上下文固化类流程。

## Instructions

### 1. 判断层级

默认写项目层。只有替换测试三问全部通过，才提交全局候选：

| 问题 | 要求 |
|------|------|
| 换技术栈仍适用吗？ | 是 |
| 换业务领域仍适用吗？ | 是 |
| 换机器或 Agent 仍适用吗？ | 是 |

### 2. 写项目层

优先追加到当前工作区 `project_context.md` 的 `## 纠正与踩坑记录`：

```markdown
### 纠正记录 YYYY-MM-DD | <一句话主题>
- 纠正前：<AI 的错误做法>
- 纠正后：<正确做法>
```

若内容已是稳定项目规则，可写入 `.agents/rules/`；若是项目工作流，可写入 `.agents/skills/`。读取时兼容历史 `.cursor/`，新增默认使用 `.agents/`。

### 3. 提交全局候选

全局候选摘要交给 `puppet-vault-curator`：

```markdown
候选名：<一句话主题>
背景：<来自哪类纠正/踩坑/成功路径>
候选规则：<去项目化后的规则文本>
替换测试：Q1 通过 / Q2 通过 / Q3 通过
证据：<workspace / conversation / 摘要>
```

### 4. 输出标记

完成项目层写入后输出：

```text
已记录：<一句话描述>
[PUPPET_INLINE_REFLECT_DONE]
```

若同时提交候选，追加 `puppet-vault-curator` 的输出标记。

## Constraints

- 不弹 AskQuestion；这是轻量记录。
- 不直接写 `rules/` 或 `skills/` 全局层。
- 不直接写 `memory/candidate_pool.jsonl`；候选池由 `puppet-vault-curator` 管理。
- 不输出 `[PUPPET_EVOLVED]`；该标记只属于 `puppet-self-evolve`。
