# Puppet 个人规则与技能库 (puppet-vault)

用于存放个人私有规则、协作 SOP 及自定义技能的本地库，实现与公司插件物理隔离。

## 核心功能
- **三步走协作模式**：针对复杂任务强制执行“诊断-竞优-迭代”流程。
- **私有规则库**：存放仅在本地生效的个人工程习惯规则。
- **自定义技能**：方便后续将重复性操作固化为本地 Skill。

## 依赖
- 需要同时安装 `sc-pipeline`
- 根入口 skill：`puppet-vault-skill`
- 清单规则：`rules/puppet-vault-plugin-manifest.mdc`

## 目录结构
- `rules/`：存放个人私有规则（.mdc）。
- `references/`：Unity/Cocos 等可扩展的详细编码规范（.md）。
- `skills/`：存放个人自定义技能（SKILL.md）。
- `scripts/`：存放技能配套的脚本。
- `sync/`：Git 同步清单（manifest.yaml）。
- `hooks/`：日级拉取与会话结束自动提交 Hook。

## GitHub 同步

- 远程仓库：[gjw843423562/puppet-vault](https://github.com/gjw843423562/puppet-vault.git)
- 同步技能：`puppet-vault-sync`
- 日级拉取：`sessionStart` Hook 自动执行（每天首次会话）
- 自动提交：`sessionEnd` Hook 检测脏改动后 commit + push
- 本地状态：`{{CURSOR_HOME}}/local_data/puppet-vault/sync_state.json`

## 个人开发约束（由 constraints.md 迁入）

| 规则文件 | 职责 |
|----------|------|
| `profile.marker` | 设备协作环境（本机 company，不反复问） |
| `rules/puppet-dev-constraints-index.mdc` | 总入口：设备/项目环境、登记簿同步、约束路由 |
| `rules/puppet-project-bootstrap.mdc` | 无项目档案时首问开发平台再开工 |
| `rules/puppet-unity-luna-compat.mdc` | Luna 打包 API 兼容（FindObjectsOfType 等） |
| `rules/puppet-modification-ledger.mdc` | 问题修改登记闭环、四列对账表 |
| `rules/puppet-unity-dev-constraints.mdc` | Unity 参数中文化、编译自检、规范加载 |
| `rules/puppet-cocos-dev-constraints.mdc` | Cocos 编译自检、规范加载 |
| `rules/puppet-refactor-gate.mdc` | 重构前必须询问用户 |
| `references/unity_rules.md` | Unity CoreRules + CodingStandards（含试玩/物理扩展） |
| `references/cocos_rules.md` | Cocos CoreRules + CodingStandards（含交付登记扩展） |

来源：`constraints.md` + `Downloads/unity_rules.md` + `Downloads/cocos_rules.md`，已统一迁入 puppet-vault `references/`。

## 说明
- 由 `sc-sop-plugin-factory` 生成的 SOP 插件骨架。
- 生成的 launcher `SKILL.md` 仅描述 SOP 入口职责，不承载业务算法。
- 生成的清单规则负责首轮输出中的插件名/版本读取，launcher 仅负责启动门槛。
