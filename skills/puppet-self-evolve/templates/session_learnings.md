# EvoNotes 自进化草稿 (sc-evolution/memory)

> **定位**：这是自进化的**临时暂存区（草稿）**，不是通用记忆库。
>
> - ✅ 适合写入：AI 行为纠正记录、协作踩坑、待评估是否升为 Rule/Skill 的经验
> - ❌ 不适合写入：用户偏好、硬约束、已验证事实 → 这些应写入 `sc-memory-layered`
>
> **生命周期**：暂存 → 聚合计数 → 成熟判断 → AskQuestion 确认后升为 Rule/Skill（或判定不适合则标记 rejected）
> **来源**：sc-evolution-curator 写入/聚合；sc-self-evolve 只处理成熟候选或用户显式全局固化

---

## 格式

```markdown
### YYYY-MM-DD | <一句话主题>

**类型**：GlobalCandidate

**触发次数**：1

**成熟度**：candidate / mature / rejected

**证据**：
- <conversation_id> / <workspace> / <一句话摘要>

**候选规则**：
<去项目化后的规则文本>

**处理记录**：
- candidate：待继续收集证据
- mature：已达到成熟门禁，等待 sc-self-evolve 确认
- rejected：不适合固化，原因：<原因>
```

---

## 记录

<!-- AI 每次发现 AI 行为层面的经验后追加到此处 -->
<!-- 用户偏好/约束/事实 请写入 sc-memory-layered，不要写在这里 -->
