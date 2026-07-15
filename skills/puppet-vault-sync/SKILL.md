---
name: puppet-vault-sync
description: "puppet-vault 个人规则库 Git 同步技能。触发：绑定 GitHub、拉取/推送规则与技能、日级自动同步、同步状态检查、手动 init/pull/push 时。须读全文获取 init/pull/push/status 命令与 manifest 白名单约束。"
---

# puppet-vault-sync

## 定位

将本机 `<vault_root>` 与个人 GitHub 仓库双向同步。`<vault_root>` 表示 puppet-vault 唯一正本目录；可由 `PUPPET_VAULT_ROOT` 显式指定，未指定时由脚本所在目录自动推导。

| 方向 | 时机 |
|------|------|
| **Pull** | 每天首次 `sessionStart` 自动执行 |
| **Commit + Push** | `sessionEnd` 检测到脏改动时自动执行 |
| **手动** | 用户说「同步 puppet-vault」「拉取规则库」「推送规则库」 |

## 远程仓库

- URL：`https://github.com/gjw843423562/puppet-vault.git`
- 分支：`main`
- 配置源：`profile.marker` → `sync_policy` 与 `sync/manifest.yaml`

## Instructions

### 1. 脚本路径

`<skill_root>` 表示当前技能自身运行态根目录。Cursor/Codex 均应通过入口链接到 `<vault_root>/skills/puppet-vault-sync/`，禁止把某个平台目录当作唯一正本。

| 平台 | 命令 |
|------|------|
| Windows | `<skill_root>/scripts/puppet_sync.cmd <action>` |
| 通用 | `python3 <skill_root>/scripts/puppet_sync.py <action>` |

### 2. 子命令

| 子命令 | 作用 |
|--------|------|
| `init` | 初始化 Git 并绑定 origin |
| `pull` | 从 GitHub 拉取（`--force` 忽略本地脏改动） |
| `push` | 推送到 GitHub |
| `commit` | 仅提交本地改动 |
| `status` | 查看同步状态 |
| `daily-pull` | 日级门禁拉取（Hook 内部使用） |
| `session-end` | 脏改动自动 commit + push（Hook 内部使用） |

### 3. 同步范围

以 `sync/manifest.yaml` 为准：

- **同步**：`rules/`、`skills/`、`references/`、`sync/`、`hooks/`、`.cursor-plugin/plugin.json`、`profile.marker`
- **不同步**：`memory/`、`**/pipeline.json`、临时文件

### 4. 与自进化衔接

- `puppet-self-evolve` 写入全局规则后，`sessionEnd` 会自动 commit + push
- 晋升到公司仓库仍走 `sc-promote-to-repo`，**不经过** puppet-vault 远程

### 5. 自管理入口

- 不使用 CCSwitch 或其他第三方 Skill 管理器作为分发前提。
- Cursor/Codex 入口由 `<vault_root>/scripts/install_agent_entries.py` 生成或修复。
- 规则正文仍在 `<vault_root>/rules`，Skill 不承担 Rule 的唯一加载职责。

## Trigger Examples

- "同步 puppet-vault 到 GitHub"
- "拉取最新个人规则库"
- "检查 puppet-vault 同步状态"
- "绑定 puppet-vault Git 仓库"

## Constraints

- 自动 push 前须确认无敏感文件（密钥、token）
- `memory/` 默认不进 Git
- 拉取时若本地有未提交改动，默认跳过 pull（避免覆盖）
- Windows Git 提交若需手动操作，优先走 `sc-git-commit` 技能
