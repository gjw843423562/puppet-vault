# TLabel 自定义标签脚本 (Puppet 规范组件)

> 路径：`{{CURSOR_HOME}}/plugins/local/puppet-vault/references/tlabel_scripts.md`
> 用于在 Unity Inspector 中显示中文名称，且不产生原生 `[Header]` 的额外间距。

## 1. TLabelAttribute.cs

```csharp
using UnityEngine;

/// <summary>
/// 自定义 Inspector 标签属性：用于在 Inspector 中显示中文名称，不产生额外间距。
/// version 2026.06.24 author AI
/// </summary>
public class TLabelAttribute : PropertyAttribute {
    public string Name;
    public TLabelAttribute(string name) {
        this.Name = name;
    }
}
```

## 2. TLabelDrawer.cs (须放在 Editor 目录下)

```csharp
using UnityEditor;
using UnityEngine;

/// <summary>
/// TLabelAttribute 的编辑器绘制器。
/// version 2026.06.24 author AI
/// </summary>
[CustomPropertyDrawer(typeof(TLabelAttribute))]
public class TLabelDrawer : PropertyDrawer {
    public override void OnGUI(Rect position, SerializedProperty property, GUIContent label) {
        TLabelAttribute labelAttribute = (TLabelAttribute)attribute;
        label.text = labelAttribute.Name;
        EditorGUI.PropertyField(position, property, label, true);
    }

    public override float GetPropertyHeight(SerializedProperty property, GUIContent label) {
        return EditorGUI.GetPropertyHeight(property, label, true);
    }
}
```
