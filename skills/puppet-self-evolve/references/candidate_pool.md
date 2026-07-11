# 全局候选池 (candidate_pool.md)

> **定位**：由 `sc-evolution-curator` 独占管理的 GlobalCandidate 候选条目暂存区。
>
> - ✅ 写入者：仅 sc-evolution-curator
> - ✅ 读取者：sc-evolution-curator（查重/成熟判断）、sc-self-evolve（弹框确认时读取候选规则）
> - ❌ 不得写入：用户偏好、项目专属经验、EvoNotes 草稿（这些写 session_learnings.md）
>
> **格式约束**：每条必须包含所有规定字段，字段名和冒号必须精确匹配，供脚本解析。

---

## 格式规范

```markdown
### YYYY-MM-DD | <候选名（一句话主题）>

**类型**：GlobalCandidate
**触发次数**：<N>
**成熟度**：candidate / mature / rejected
**证据**：
- <conversation_id> / <workspace> / <一句话摘要>
**候选规则**：
<去项目化后的规则文本，不含具体路径/表名/人名/项目名>
```

---

## 候选条目

<!-- sc-evolution-curator 写入，不要手动编辑 -->
