# puppet-vault Cursor 入口说明

Cursor 只作为运行入口，不保存规则或技能的第二份正文。

## 正本目录

`<vault_root>` 表示 puppet-vault 唯一正本目录，例如当前机器为：

```text
D:\puppet-vault
```

## 入口目录

Cursor 运行入口位于：

```text
{{CURSOR_HOME}}/plugins/local/puppet-vault/
```

该目录下核心子目录应链接到 `<vault_root>`：

```text
.cursor-plugin/
references/
rules/
scripts/
skills/
sync/
```

## 入口修复

若 Cursor 插件入口丢失，在 `<vault_root>` 下运行：

```bat
scripts\install_agent_entries.cmd --agents cursor
```

或：

```bash
python3 scripts/install_agent_entries.py --agents cursor
```
