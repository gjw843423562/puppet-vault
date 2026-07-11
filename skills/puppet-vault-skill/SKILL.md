---
name: puppet-vault-skill
description: Puppet 个人规则与技能库 SOP 启动技能。用户提到 Puppet 个人规则与技能库、用于存放个人私有规则、协作 SOP 及自定义技能的本地库，实现与公司插件物理隔离。、执行 puppet-vault-skill 等意图时，进入本技能作为统一入口；本技能通过 pipeline 方式接力已有子 skill，避免跳步和子 skill 直连。前置：一旦按本技能执行，须先用 read_file 读全文本插件清单规则，相对本 SKILL.md 的路径为 ../../rules/puppet-vault-plugin-manifest.mdc，再按其正文继续（含 plugin.json 与首轮输出）。
---

# puppet-vault-skill

## 前置条件（须先于 Instructions 内任一步）

1. 仅凭规则索引里的 `description` **不算**已加载正文；必须先 **`read_file`** 读取下面规则文件的**全文**。
2. **规则文件路径（相对路径，以本文件 `SKILL.md` 所在目录为锚点）**：`../../rules/puppet-vault-plugin-manifest.mdc`
   - 含义：`SKILL.md` 在 `skills/puppet-vault-skill/` → `../..` 到插件根目录 → `rules/puppet-vault-plugin-manifest.mdc`。
3. 读完该规则后，**严格按其正文**完成后续要求（例如读取本机 `plugin.json` 的 `name`/`version` 及首轮输出格式），**再**进入下方 **Instructions**。

## Instructions

### 1. 触发判定

1. 识别到“Puppet 个人规则与技能库 + SOP/流程/执行”相关意图时，进入本技能。
2. 若用户只提到某个子步骤，但目标仍是 Puppet 个人规则与技能库 主链，也应优先进入本技能，不得直接跳到子 skill。

### 2. 启动方式（启动器模式）

1. 必须且只能调用共享启动辅助工具 `{{CURSOR_HOME}}/hooks/scripts/pipeline_skill_bootstrap.py` 启动当前技能对应的管线；执行时传入 `--project-root <根目录>` 与 `--skill-root <skill_root>`，必要时再显式补 `--root-skill <技能名>`。其中 `<skill_root>` 表示“当前技能自身的运行态根目录”，执行前应先展开，而不是按当前工作区猜路径。底层 `pipeline_launcher.py` 与流程配置文件由该辅助工具在内部处理。**必须通过 `python3` 解释器执行**（禁止用 `python` 或 `py` 别名，防止环境不一致或版本混乱）。
2. 启动完成后，Agent 必须立即结束当前轮，不做额外总结，由 stop hook 触发后续接力。

### 3. 运行规范（黑盒模式）

1. 任务（包括后续原子技能）完成后，必须且只能输出一句：“**后续流程将由系统 hook 自动接力。**” 然后立即闭嘴，静默等待。
2. 后续流程由底层 Hook 系统接管并自动弹窗下发，严禁自行“预判”或“推进”。

## Trigger Examples

- "执行 Puppet 个人规则与技能库 SOP"
- "帮我跑一遍 Puppet 个人规则与技能库 流程"
- "启动 puppet-vault-skill"

## Constraints

- 【黑盒禁区】这是一条纯物理控制的管线，你不需要也不允许知道它的配置与进度。
- 禁止绕过本技能直接触发下游子 skill。
- 严禁读取、修改或使用工具探测 `pipeline.json` 与 `.cursor/pipeline/` 目录下的任何文件。
- 严禁在完成任务后输出“下一步我将做什么”或“开始执行 @xxx”，必须使用统一收尾话术并等待系统通知。
- 严禁为了“跑通流程”而尝试去创建任何后缀为 `.json` 的完成锚点文件。
