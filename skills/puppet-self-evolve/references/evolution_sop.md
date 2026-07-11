# 自进化产出 SOP (evolution_sop)

> 何时读：需要执行 Rule/Skill/EvoNotes 产出流程，或需要了解 sc-evolution 结构时。

---

## 核心原则

> 自进化产物先做**范围分层**：只在当前项目成立的内容写当前工作区；跨项目仍成立、但尚未晋升仓库的内容写本机私有插件 `sc-evolution`。
> 若用户**明确要求**「直接固化到通用仓库」，可直接写 `publish_dir/plugins/**`，但必须先完成插件路由、二次判断与发布层清洗。

---

## 分层落点

### 项目层（当前工作区）

```
<workspace>/
├── .agents/rules/
├── .agents/skills/
├── .agents/hooks/
├── .agents/scripts/
└── project_context.md
```

说明：`.agents/` 是新增和迭代的默认目录；扫描、比对、晋升旧项目经验时仍须兼容历史 `.cursor/rules/` 与 `.cursor/skills/`，避免漏读旧 rule/skill。

### 全局私有层（sc-evolution）

```
Cursor: {{CURSOR_HOME}}/plugins/local/sc-evolution/
Codex/Claude/Gemini: {{AGENTS_HOME}}/local_data/sc-evolution/
```

Windows 示例：Cursor 使用 `%USERPROFILE%\.cursor\plugins\local\sc-evolution\`；Codex 使用 `%USERPROFILE%\.codex\local_data\sc-evolution\`

**为什么这个路径**：Cursor 自动加载本机插件目录的 `rules/` 和 `skills/`；不在同步工具覆盖范围内；每台机器独立维护。

### 直接发布层（仅用户显式要求）

```
publish_dir/plugins/<plugin>/
```

仅当用户明确要求“不需要先到私有目录再晋升”时使用；仍需补做发布层清洗。

### 目录结构

```
sc-evolution/
├── .cursor-plugin/
│   └── plugin.json              # 插件清单（Cursor 识别入口）
├── EVOLUTION_LOG.md             # 进化日志（每次产出追加一行）
├── rules/                       # 自动生成的规则（.mdc）
│   └── YYYY-MM-DD_<topic>.mdc
├── skills/                      # 自动生成的技能
│   └── <skill-name>/SKILL.md
└── memory/                      # EvoNotes 草稿（待晋级暂存区）
    └── session_learnings.md
```

---

## 产出分类

| 触发场景 | 类型 | 项目层目标 | 全局/发布目标 |
|---------|------|------------|----------------|
| AI 被纠正行为/口径/工具选择 | Rule（`.mdc`） | `<workspace>/.agents/rules/`，读取兼容旧 `.cursor/rules/` | `sc-evolution/rules/` 或直接发布到 `publish_dir/plugins/<plugin>/rules/` |
| 找到可复用成功工作流 | Skill（`SKILL.md`） | `<workspace>/.agents/skills/<name>/`，读取兼容旧 `.cursor/skills/` | `sc-evolution/skills/<name>/` 或直接发布到 `publish_dir/plugins/<plugin>/skills/<name>/` |
| 当前项目的文档树 / 目录锚点 / 业务口径 | Context/知识 | `<workspace>/project_context.md` | 不应直接写入公共层 |
| AI 行为教训，尚未确定是否升为 Rule/Skill | EvoNotes（草稿） | 先写项目上下文或待确认清单 | `memory/session_learnings.md` |

### EvoNotes vs sc-memory-layered 边界

| 维度 | EvoNotes（sc-evolution/memory） | sc-memory-layered（长期 Vault） |
|------|--------------------------------|-------------------------------|
| 内容性质 | AI 行为纠正、协作踩坑、待晋级草稿 | 用户偏好、硬约束、已验证事实 |
| 生命周期 | 短暂：升为 Rule/Skill 后可删 | 永久：跨会话跨 Agent 复用 |
| 决策口诀 | "AI 以后要**怎么做**" | "AI 以后要**记住什么**" |

---

## 命名规范

**Rule**：`YYYY-MM-DD_<触发场景（英文连字符）>.mdc`
```
✓ 2026-04-13_svn-commit-encoding-workaround.mdc
✗ fix.mdc  / 规则1.mdc
```

**Rule 内容模板**：
```yaml
---
description: "<一句话描述>（自进化 YYYY-MM-DD，验证 N 次）"
alwaysApply: true
---

# <规则标题>

## 触发场景
<什么协作问题导致了这条规则>

## 规则内容
<具体约束>

## 来源
- 发现时间：YYYY-MM-DD
- 验证次数：1（初始）
```

**Skill**：小写连字符目录名，体现功能非时间
```
✓ skills/git-amend-recovery/SKILL.md
✗ skills/2026-04-13-skill/SKILL.md
```

**Skill SKILL.md 头部追加**：
```yaml
metadata:
  evolution:
    source: sc-meta-optimizer
    created: YYYY-MM-DD
    verified_count: 1
    promote_to_repo: false
```

---

## 执行步骤（Step E0–E6）

### Step E0：运行 check_init 平台入口

```bash
# 已知当前项目根目录时：
"<skill_root>/scripts/check_init.cmd" --workspace "<workspace>"
sh "<skill_root>/scripts/check_init.sh" --workspace "<workspace>"

# 仅处理全局层时：
"<skill_root>/scripts/check_init.cmd"
sh "<skill_root>/scripts/check_init.sh"
```

Windows 默认入口使用 `check_init.cmd`；WSL/Linux/macOS 默认入口使用 `check_init.sh`。两者均优先解析 Python3，避免误命中 Python2。
若 `<skill_root>` 是符号链接目录，Linux/WSL/macOS 下检查脚本存在性时使用 `find -L` 或 `readlink`，不要用普通 `find` 的空结果判断脚本缺失。
仅在诊断/兜底排障时，才允许直调主体 Python：

```bash
python "<skill_root>/scripts/check_init.py" --workspace "<workspace>"
```

- 自动创建 sc-evolution（若不存在），从 `templates/` 读取所有模板文件
- 扫描现有 `rules/*.mdc` 和 `skills/*/SKILL.md`，返回描述摘要
- 若提供 `--workspace`，同步扫描当前项目的 `.agents/rules/`、`.agents/skills/`、历史 `.cursor/rules/`、历史 `.cursor/skills/` 与 `project_context.md`
- 输出 `[AI_HINT]`：先判定项目层 / 全局层，再比对是否已有可迭代项

输出示例：
```
[INIT_STATUS] already_exists
[EVOLUTION_PATH] C:\Users\...\sc-evolution
[WORKSPACE_PATH] E:\DataAI
[PROJECT_CONTEXT] exists
[EXISTING_RULES]
  - 2026-04-13_svn-encoding.mdc: SVN 提交编码问题（验证 2 次）
[EXISTING_PROJECT_RULES]
  - doc-index-routing.mdc: 新增文档前先检查根索引
[EXISTING_SKILLS]
  (空)
[EXISTING_MEMORY_ENTRIES] 3
[AI_HINT] 先判断项目层 / 全局层；若当前经验只在本项目成立，优先迭代项目层已有文件。
```

### Step E1：分析当前对话，提取固化内容

回顾本轮触发点：被纠正了什么？找到什么成功路径？有什么踩坑教训？

输出一句话摘要：**「[触发类型] | [范围:项目/全局/待判断] → [描述]」**

### Step E2：先定范围，再判断新建 vs 迭代

先给出分类结论：

`分类结论：类型=<Rule/Skill/Context>｜范围=<项目/全局/直接发布>｜写入目标=<精确路径>｜不选另一层原因=<一句话>`

| 条件 | 行动 |
|------|------|
| 无现有内容 / 描述完全不重叠 | **新建** |
| 有相似 description（触发场景一致 OR 重叠 > 50%） | **迭代**：patch 现有文件，`verified_count` +1 |
| 有相关但不完全重叠 | **新建** + 引用已有 |

### Step E3：写入文件

**项目 Rule**：`<workspace>/.agents/rules/<topic>.mdc`
读取旧资料时兼容 `<workspace>/.cursor/rules/<topic>.mdc`。

**全局 Rule**：Cursor 使用 `{{CURSOR_HOME}}/plugins/local/sc-evolution/rules/YYYY-MM-DD_<topic>.mdc`；其他 Agent 使用 `{{AGENTS_HOME}}/local_data/sc-evolution/rules/YYYY-MM-DD_<topic>.mdc`
- 必须含：description（frontmatter）、触发场景、规则内容、来源

**直接发布 Rule**：`publish_dir/plugins/<target-plugin>/rules/<topic>.mdc`
- 落盘前必须先做发布层清洗：去掉私有流程名、验证态措辞、来源痕迹

**项目 Skill**：`<workspace>/.agents/skills/<name>/SKILL.md`
读取旧资料时兼容 `<workspace>/.cursor/skills/<name>/SKILL.md`。

**全局 Skill**：Cursor 使用 `{{CURSOR_HOME}}/plugins/local/sc-evolution/skills/<name>/SKILL.md`；其他 Agent 使用 `{{AGENTS_HOME}}/local_data/sc-evolution/skills/<name>/SKILL.md`
- 必须含：`metadata.evolution`

**直接发布 Skill**：`publish_dir/plugins/<target-plugin>/skills/<name>/SKILL.md`
- 同样必须先完成二次判断与发布层清洗

**EvoNotes**：Cursor 使用 `{{CURSOR_HOME}}/plugins/local/sc-evolution/memory/session_learnings.md`；其他 Agent 使用 `{{AGENTS_HOME}}/local_data/sc-evolution/memory/session_learnings.md`
- 仅用于全局层待判断草稿
- 若内容是用户偏好/硬约束 → 改用 `sc-memory-layered`，不写这里

### Step E4：追加进化日志

在 `EVOLUTION_LOG.md` 的记录表末尾追加：
```markdown
| YYYY-MM-DD | Rule/Skill/EvoNotes | 文件名 | 触发原因 | 1 | 待评估 |
```

迭代时更新对应行的验证次数。

### Step E5：用户可见反馈

```
✅ 已自进化：[新建/迭代] [类型] → [文件名]
   摘要：[一句话]
   路径：[完整绝对路径]
   已追加进化日志。
```

禁止：静默完成不反馈、不展示路径。

### Step E6：评估提升（非阻塞）

若该条目验证次数 ≥2，在反馈末追加：
> 「该 [Rule/Skill] 已验证 N 次，是否提升到 `cursor-tool-sync-publish`？（是→告诉我执行）」

---

## 提升到通用仓库的标准

| 维度 | sc-evolution（私有） | cursor-tool-sync-publish（通用） |
|------|---------------------|-------------------------------|
| 通用性 | 可含本机特有场景 | 与机器/用户/项目无关 |
| 验证次数 | 1 次 | ≥2 次，不同场景均有效 |
| 敏感信息 | 无要求 | 必须脱敏，使用 `{{CURSOR_HOME}}` 等模板变量 |
| 质量 | 无硬性要求 | 符合 sc-skill-creator 六维质量标准 |

**提升路径**：
1. 复制到 `publish_dir/plugins/<目标插件>/rules/` 或 `skills/`
2. 脱敏、补全质量字段
3. 提交发布仓库，同步工具分发到运行态
4. `EVOLUTION_LOG.md` 中该条"是否提升"更新为"已提升"

---

## v0.6 三级标记联动（当前路径）

自进化不再由 stop hook 或工具事件直接拉起完整固化流程，而是采用三段式成熟模型：

| 阶段 | 组件 | 动作 | 输出标记 |
|------|------|------|----------|
| 对话内轻量反思 | `sc-inline-reflect` | 写项目层纠正/踩坑/成功路径；有全局价值时提交候选摘要 | `[SC_INLINE_REFLECT_DONE]` |
| 候选池成熟化 | `sc-evolution-curator` | 写入或聚合 `GlobalCandidate`，更新触发次数，判断成熟度 | `[SC_CANDIDATE_DRAFTED]` |
| 全局进化确认 | `sc-self-evolve` | 仅在用户显式要求或 curator 提交成熟候选时，AskQuestion 确认后写全局 | `[SC_EVOLVED]` |

`sessionStart` 只注入 F 节，让 AI 知道上述链路。`stop` hook 只检查最后一条 AI 回复中的标记组合并做兜底提醒：无反思则短 followup 要求补扫；有草稿无进化则提示“可按需调用 sc-self-evolve”；它不直接写经验、不直接弹 AskQuestion、不直接启动 E0-E6。

**与专项技能的协作边界**：
- `sc-inline-reflect`：项目层即时记录，不写全局候选池条目
- `sc-evolution-curator`：候选池查重、聚合、成熟度判断，不写全局 Rule/Skill
- `sc-skill-creator`：执行技能创建/优化
- `sc-rule-skill-decider`：判断该建 Rule 还是 Skill
- `sc-memory-layered`：写入个人偏好、长期约束和跨会话记忆
