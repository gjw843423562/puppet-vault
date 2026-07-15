# puppet-vault 自管理运行方案

## 决策

`puppet-vault` 不交给 CCSwitch 或其他第三方 Skill 管理器分发。仓库自身维护规则、技能、脚本和平台入口，避免未来更换 AI 工具时被某个管理器绑定。

## 唯一正本

`<vault_root>` 表示 puppet-vault 的唯一正本目录，例如当前机器为：

```text
D:\puppet-vault
```

所有规则、技能、脚本和引用资料均以 `<vault_root>` 为准。

## 平台入口

Cursor 与 Codex 只保留入口，不维护第二份正文。

| 平台 | 入口 | 指向 |
|------|------|------|
| Cursor | `{{CURSOR_HOME}}/plugins/local/puppet-vault/{rules,skills,scripts,references,sync,.cursor-plugin}` | `<vault_root>` 对应目录 |
| Codex | `{{AGENTS_HOME}}/skills/puppet-*` 或 `%USERPROFILE%/.codex/skills/puppet-*` | `<vault_root>/skills/puppet-*` |

## 安装命令

Windows:

```bat
scripts\install_agent_entries.cmd --agents cursor,codex
```

通用:

```bash
python3 scripts/install_agent_entries.py --agents cursor,codex
```

可选环境变量：

| 变量 | 作用 |
|------|------|
| `PUPPET_VAULT_ROOT` | 显式指定唯一正本目录 |
| `PUPPET_VAULT_STATE_HOME` | 指定同步状态和日志目录 |
| `AGENTS_HOME` | Codex/Claude/Gemini 等 Agent 的用户级目录 |
| `CURSOR_HOME` | Cursor 用户级目录 |

## 规则移植原则

规则不伪装成 Skill。Rule 是前置约束，Skill 是触发后执行能力。

- Cursor 通过 `.mdc` 规则入口加载或按需读取 `<vault_root>/rules`。
- Codex 通过 `AGENTS.md` 或会话注入桥接 `<vault_root>/rules`。
- Skill 只放可执行流程，不承担硬性行为约束的唯一入口。

## 后续新增内容

新增 Rule/Skill/Script 时优先写入 `<vault_root>`：

```text
rules/
skills/
scripts/
references/
```

平台适配只更新入口或说明，不复制正文。
