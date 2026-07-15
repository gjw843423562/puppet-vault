# Project Rules for Unity & C# (Global constraints)

> Puppet 规范库。路径：`<vault_root>/references/unity_rules.md`
> 与 `rules/puppet-unity-dev-constraints.mdc` 联动；后者为硬约束入口（参数中文化、编译自检、登记闭环）。

当在电脑上使用 Cursor 协作 Unity/C# 项目时，必须严格加载并遵守此规则。

==================================================
## ⚖️ 规则优先级声明（最高级）
当 CoreRules 与 CodingStandards 冲突时：
✅ 必须以 CoreRules 为最高执行优先级。
✅ CodingStandards 不得覆盖核心行为规则。
==================================================

## 🎯 CoreRules_Unity (模式：Always)
1. **中文交流**：所有的思考、回答、方案设计、代码注释及文档撰写必须统一使用中文。
2. **未确认禁止改代码**：未经用户在对话中明确授权确认，严禁修改项目内的任何脚本。
3. **Markdown方案先行**：所有修改在执行前，必须首先生成详细的 Markdown 方案说明。
4. **禁止主动创建脚本**：严禁主动新建 C# 脚本，除非用户在指令中明确提出该要求。
5. **代码极致精炼**：所有编写的代码必须极致精炼，严禁出现任何冗余或重复的底层逻辑。
6. **强制#region中文分类**：脚本内的功能区块必须强制使用 `#region 标题` 进行分类，且 region 标题名必须为中文。
7. **评估系统影响**：修改任何功能前，必须科学评估其对已有系统的影响，严禁破坏既有功能。
8. **提供模拟测试流程**：修改完成后，必须提供包含测试目标、环境、步骤、预期和风险点的完整测试流程。
9. **禁止猜测需求**：遇到任何含糊、不明确的口径或业务定义时，禁止主观猜测，必须先向用户提问。
10. **修改必须可回滚**：所有修改方案必须具备完备的可回滚性，提供备份或逆向恢复路径。
11. **覆盖异常路径**：必须对所有关键逻辑和 IO 操作进行异常捕获、异常路径和失败降级处理。
12. **AI代码必须带注释**：由 AI 生成或修改的类、方法和复杂功能，必须包含清晰的结构化注释，**方法必须注释其功能，代码内部也需要详细注释说明具体用途**，禁止生产无注释代码。

==================================================

## 📂 FileRules_Unity (模式：Auto Attached)
* **匹配范围**：对工程中所有 `Assets/**/*.cs` 文件自动关联并强制执行本规则。

==================================================

## 💎 CodingStandards_Unity (模式：Always)

### 1. 命名与前缀规范
* **类与文件命名**：必须使用 **PascalCase**。场景脚本必须与 Scene 同名，Prefab 控制脚本必须与预制件同名。
* **特定前缀**：工具类用 `T`，基类用 `Base`，界面层用 `Layer`，通知/弹窗用 `Notify`，常量类用 `Const`，接口用 `I`，枚举用 `Enum`。严禁 AI 自创命名流派。
* **变量命名**：公共变量/属性使用 **PascalCase**，私有/受保护变量使用 **_camelCase**。严禁使用 `m_xx`。
* **变量类型前缀（推荐）**：`s` (string), `b` (bool), `i` (int), `f` (float), `d` (dictionary/JSON), `l` (list/array), `o` (object), `v2/v3` (vector)。
* **函数命名**：公共函数用 **PascalCase**，私有函数用 **_camelCase**，回调函数用 **on** 前缀（如 `onNextClick`）。每个函数必须单一职责，通常不超过 80 行。

### 2. 注释规范
* AI 生成的代码必须包含结构化头注释：
  ```csharp
  /// <summary>
  /// 功能说明
  /// version yyyy.MM.dd author AI
  /// </summary>
  ```
  复杂逻辑或版本迭代必须记录详细的修改日志和版本说明。

### 3. 常量、配置与禁用法则
* **严禁硬编码**：任何数值、配置和字符串严禁硬编码在业务层，必须统一在 `GameConfig`、`Consts` 或 `DataManager` 中进行配置化管理。
* **禁用法则**：禁止临时测试代码，禁止提交未完成的 `TODO`。非算法必要，禁止使用不易读的位运算。字符串拼接必须统一使用插值表达式 `$""`。

### 4. 边界保护与性能优化
* **边界安全**：数值计算和数据越界必须强制进行 `Clamp`（限制在最大/最小值）并输出 `Debug.LogWarning`。严禁发生数组越界。
* **性能红线**：
  * 🔴 **严禁在 Update/LateUpdate 等高频循环中执行 GetComponent / Find 等操作**；
  * 🔴 避免在循环或 Update 内频繁执行 `new` 操作；
  * 🔴 针对高频创建和销毁的粒子、子弹和特效等物体，**必须强制使用对象池（Object Pool）**；
  * 🔴 能够在 Awake / Start 缓存的引用必须提前缓存。

==================================================

## 🔧 Puppet 扩展：预制体/场景优先（禁止脚本叠补丁）

- 若问题可通过 **Prefab 或 Scene**（禁用/删除冗余节点、修正 Inspector 引用、Button OnClick、层级显隐等）解决，**必须优先在资源侧修复**。
- **禁止**为同一根因叠加脚本运行时补丁（如 `OnShow` 里 `Find` 藏节点、全局标志位改其他模块行为）。
- 脚本只写 Prefab 无法表达的**业务逻辑**（计奖、存档、流程跳转）。决策与反模式详见 `puppet-unity-dev-constraints.mdc`「预制体/场景优先」节。

## 🔧 Puppet 扩展：Inspector 与序列化

- 对外暴露的 Inspector 参数必须中文化。
- **推荐方案**：使用自定义 `[TLabel("中文名称")]` 属性。该方案无额外间距，视觉效果极佳，且不依赖第三方插件。源码参考：`<vault_root>/references/tlabel_scripts.md`。
- **备选方案**：使用 Unity 原生 `[Header("中文名称")]` / `[Tooltip("中文说明")]`。
- **个人项目例外**：若是个人项目且已安装 Odin，可优先考虑 Odin 的序列化插件（如 `[LabelText]`）。
- **严禁**：在未获授权的公司项目中擅自引入第三方序列化插件。

## 🔧 Puppet 扩展：试玩 / 物理 / WebGL 专项

1. **物理脚本安全**：涉及 `FixedUpdate`/`LateUpdate` 的高频物理脚本，禁止小片段 StrReplace 改核心循环；须全文读取后整体重写。
2. **AI 输入隔离**：AI 控制分支须检查 `isAIControlled`，禁止玩家输入静默覆盖 AI 的 accel/steer/brake。
3. **WebGL/Luna 兼容**：禁用 `System.IO.File` 写调试日志（会 Not implemented）；埋点仅用 `Debug.Log` + `[DBG<sessionId>]` 前缀 + 单行 NDJSON（细则见 `puppet-unity-dev-constraints.mdc`「WebGL / Luna 运行时调试日志」）；类名混淆下禁止依赖 `GetType().Name` 查找组件。
4. **路点 AI**：禁止依赖节点名称解析索引；使用 `currentIndex` 递增/递减并做边界 Clamp。
5. **路点到达判定**：不可仅依赖 Distance；须配合 Local Z 或 Dot Product 判定「点在身后」。
6. **Web 速度解耦**：速度模长与前进方向分开平滑，防止连续大角转向时速度塌陷。
7. **Web 垂直速度**：斜面投影驱动时禁止重复累加 `currentVelocity.y`，防止双倍向上推力。

## 🔧 Puppet 扩展：交付与登记

- 脚本修改完成后须编译通过（Unity 唤醒编译或 ReadLints）再交付。
- Bug/功能修改落地后须走 `puppet-modification-ledger.mdc` 登记闭环。

<!-- PUPPET_UNITY_RULES_EXTEND_START -->
<!-- PUPPET_UNITY_RULES_EXTEND_END -->
