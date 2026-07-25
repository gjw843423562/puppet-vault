---
name: puppet-engineering-efficiency
description: "Puppet 个人工程提效底座技能。触发：编写/维护 Windows Shell、Python 工具脚本、puppet-vault 同步脚本、候选池脚本、Git 自动化，或遇到编码、路径、Python2/3、脚本入口、提交同步安全问题时。须读全文获取 Windows/Git/Python 三类规则路由、执行前检查、脚本自测与阶段同步策略。"
---

# Puppet 工程提效底座

## 定位

把个人库中高频工程坑位集中路由：Windows Shell、Git 同步、Python 工具脚本。它不替代具体任务 Skill，只负责在动手前加载正确规则并给出最低验收。

## 规则路由

| 场景 | 必读规则 |
|------|----------|
| `.cmd` / `.bat` / `.ps1`、中文路径、删除目录、后台启动 | `rules/puppet-windows-shell-safety.mdc` |
| puppet-vault 同步、自动 commit/push、工作区有脏改动 | `rules/puppet-git-sync-safety.mdc` |
| `skills/**/scripts/*.py`、Python 入口、Python2/3 冲突 | `rules/puppet-python-tooling-standard.mdc` |

## Instructions

### 1. 执行前检查

1. 确认目标仓库和工作区。
2. 若涉及写文件，确认路径位于用户授权工作区。
3. 若涉及 Git，同步前检查是否有用户已有脏改动。
4. 若涉及脚本，先判断是否应“轻入口 + 重 Python”。

### 2. 实现约束

- CMD/SH 只做入口层。
- Python 工具脚本默认兼容 Python 3.8。
- 删除目录不走 Shell 递归删除。
- Git 有无关脏改动时只 stage 本阶段文件。

### 3. 验证清单

| 变更类型 | 最低验证 |
|----------|----------|
| Python CLI | `python3 script.py --help` |
| Windows 入口 | `script.cmd --help` |
| Git 阶段同步 | dry-run、提交消息校验、push 成功 |
| 规则/Skill 文档 | 回读正文，检查 description 与触发词 |

### 4. 阶段同步

当用户要求“每完成一步后同步 Git”时：

1. 每阶段只提交本阶段文件。
2. 提交后立即 push。
3. 若同步脚本会包含无关脏改动，改用显式暂存，并说明原因。
4. 阶段失败时不进入下一阶段。

## Trigger Examples

- "写个 puppet 工具脚本。"
- "这个 cmd 入口不稳定，帮我整理。"
- "同步 puppet-vault，但别带上其他脏文件。"
- "Python 报语法错，好像版本不对。"

## Constraints

- 不绕过三条底线规则。
- 不默认安装依赖或强推远端。
- 不把临时运行态数据加入 Git。
- 有脚本改动时，未自测不得提交。
