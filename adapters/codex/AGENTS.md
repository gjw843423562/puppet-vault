# puppet-vault Codex 规则桥接模板

本文件用于把 puppet-vault 规则正本接入 Codex。复制或注入到 Codex 会话入口时，保持规则正文仍在 `<vault_root>`，不要在 Codex 侧维护第二份规则。

## 正本目录

`<vault_root>` 表示 puppet-vault 唯一正本目录，例如当前机器为：

```text
D:\puppet-vault
```

## Codex 启动要求

在需要使用 puppet-vault 个人规则时：

1. 先读取 `<vault_root>/rules/puppet-dev-constraints-index.mdc` 全文。
2. 根据该总入口的路由表，按场景继续读取对应子规则全文。
3. Unity/Cocos 规范引用统一读取 `<vault_root>/references/` 下的正文。
4. Skill 通过 Codex `skills/` 入口触发；Rule 不伪装成 Skill。

## 当前启用平台

当前仅启用：

- Cursor
- Codex

暂不接入 CCSwitch、Claude、Gemini 或其他 Skill 管理器。

## 入口修复

若 Codex skill 入口丢失，在 `<vault_root>` 下运行：

```bat
scripts\install_agent_entries.cmd --agents codex
```

或：

```bash
python3 scripts/install_agent_entries.py --agents codex
```
