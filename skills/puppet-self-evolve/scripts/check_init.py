# -*- coding: utf-8 -*-
"""
puppet-self-evolve: check_init.py

puppet-vault 自进化插件初始化检查与内容扫描脚本。

职责：
  1. 检测 puppet-vault 插件目录是否存在
  2. 若不存在，自动创建完整目录结构，并从 ../templates/ 读取各模板文件写入
  3. 扫描现有全局层（rules/ skills/ memory/），返回结构化摘要
  4. 若提供 --workspace，则同步扫描项目层（优先 .agents，同时兼容历史 .cursor；写入默认 .agents）
  5. 输出 AI 可直接读取的决策报告，用于先判定"项目/全局"，再判断"新建"还是"迭代"

用法：
  python check_init.py [--agents-home PATH] [--cursor-home PATH] [--evolution-home PATH] [--workspace PATH]

输出格式（stdout，AI 逐行读取）：
  [INIT_STATUS] created|already_exists
  [EVOLUTION_PATH] <绝对路径>
  [WORKSPACE_PATH] <绝对路径>
  [PROJECT_CONTEXT] exists|missing
  [EXISTING_RULES]
    - <文件名>: <description>
  [EXISTING_PROJECT_RULES]
    - <文件名>: <description>
  [EXISTING_SKILLS]
    - <目录名>: <description>
  [EXISTING_PROJECT_SKILLS]
    - <目录名>: <description>
  [EXISTING_MEMORY_ENTRIES] <N>
  [AI_HINT] <决策建议>

模板文件位于：<skill_root>/templates/
  puppet-vault-plugin.json   → puppet-vault/.cursor-plugin/plugin.json
  EVOLUTION_LOG.md           → puppet-vault/EVOLUTION_LOG.md
  session_learnings.md       → puppet-vault/memory/session_learnings.md
  rules_README.md            → puppet-vault/rules/README.md
  skills_README.md           → puppet-vault/skills/README.md
"""

import os
import sys
import re
import argparse
from pathlib import Path

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("PYTHONUTF8", "1")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# templates/ 目录：与 scripts/ 同级
_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

# 模板文件名 → puppet-vault 内目标路径（相对）
_TEMPLATE_MAP = {
    "puppet-vault-plugin.json": ".cursor-plugin/plugin.json",
    "EVOLUTION_LOG.md":         "EVOLUTION_LOG.md",
    "session_learnings.md":     "memory/session_learnings.md",
    "rules_README.md":          "rules/README.md",
    "skills_README.md":         "skills/README.md",
}


# ─────────────────────────────────────────────────────────────
# 模板加载
# ─────────────────────────────────────────────────────────────

def _load_template(name: str) -> str:
    """从 templates/ 目录读取模板文件内容，读取失败时抛出 FileNotFoundError。"""
    path = _TEMPLATES_DIR / name
    if not path.exists():
        raise FileNotFoundError(
            f"模板文件缺失：{path}\n"
            f"请确认 puppet-self-evolve/templates/{name} 已正确部署到运行态。"
        )
    return path.read_text(encoding="utf-8")


# ─────────────────────────────────────────────────────────────
# 路径解析
# ─────────────────────────────────────────────────────────────

def get_agents_home() -> Path:
    """解析当前 Agent home；AGENTS_HOME 优先，CURSOR_HOME 兼容 Cursor。"""
    agents_home = os.environ.get("AGENTS_HOME")
    if agents_home:
        return Path(os.path.expandvars(agents_home)).expanduser()
    env_home = os.environ.get("CURSOR_HOME")
    if env_home:
        p = Path(os.path.expandvars(env_home)).expanduser()
        return p if p.name.lower() == ".cursor" else p / ".cursor"
    user_home = Path(os.environ.get("USERPROFILE") or os.path.expanduser("~"))
    return user_home / ".cursor"


def get_evolution_dir(agents_home: Path, explicit_home: str = "") -> Path:
    """解析 puppet-vault 运行态目录。"""
    override = explicit_home or os.environ.get("SC_EVOLUTION_HOME", "")
    if override:
        return Path(os.path.expandvars(override)).expanduser()
    if agents_home.name.lower() == ".cursor":
        return agents_home / "plugins" / "local" / "puppet-vault"
    return agents_home / "local_data" / "puppet-vault"


# ─────────────────────────────────────────────────────────────
# 初始化
# ─────────────────────────────────────────────────────────────

def ensure_evolution_plugin(evolution_dir: Path) -> str:
    """
    确保 puppet-vault 插件存在。
    返回 'created' 或 'already_exists'。
    """
    marker = evolution_dir / ".cursor-plugin" / "plugin.json"
    if evolution_dir.exists() and marker.exists():
        return "already_exists"

    # 创建所有子目录
    for subdir in [".cursor-plugin", "rules", "skills", "memory"]:
        (evolution_dir / subdir).mkdir(parents=True, exist_ok=True)

    # 从 templates/ 写入各模板文件
    errors = []
    for tpl_name, rel_dest in _TEMPLATE_MAP.items():
        try:
            content = _load_template(tpl_name)
            dest = evolution_dir / rel_dest
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")
        except FileNotFoundError as e:
            errors.append(str(e))

    if errors:
        # 部分模板缺失时仍继续，但在输出中报告
        print("[WARNING] 部分模板文件缺失，以下文件未能写入：", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)

    return "created"


# ─────────────────────────────────────────────────────────────
# 扫描现有内容
# ─────────────────────────────────────────────────────────────

def _extract_frontmatter_field(content: str, field: str) -> str:
    """从 YAML frontmatter 中提取指定字段值。"""
    pattern = rf'^{re.escape(field)}:\s*["\']?(.+?)["\']?\s*$'
    m = re.search(pattern, content, re.MULTILINE)
    return m.group(1).strip() if m else ""


def _read_description(file_path: Path) -> str:
    """读取 .mdc 或 SKILL.md 中的 description 字段。"""
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
        desc = _extract_frontmatter_field(content, "description")
        return desc if desc else "(无描述)"
    except Exception:
        return "(读取失败)"


def scan_evolution(evolution_dir: Path) -> dict:
    """
    扫描现有 puppet-vault 内容，返回摘要字典：
      rules: [{name, description}, ...]
      skills: [{name, description}, ...]
      memory_entries: int
    """
    result = {"rules": [], "skills": [], "memory_entries": 0}

    # 扫描 rules/*.mdc
    rules_dir = evolution_dir / "rules"
    if rules_dir.exists():
        for f in sorted(rules_dir.glob("*.mdc")):
            result["rules"].append({
                "name": f.name,
                "description": _read_description(f),
            })

    # 扫描 skills/<dir>/SKILL.md
    skills_dir = evolution_dir / "skills"
    if skills_dir.exists():
        for d in sorted(skills_dir.iterdir()):
            if d.is_dir() and not d.name.startswith("."):
                skill_md = d / "SKILL.md"
                desc = _read_description(skill_md) if skill_md.exists() else "(无 SKILL.md)"
                result["skills"].append({"name": d.name, "description": desc})

    # 统计 memory 条目数（按 ### 标题计）
    memory_file = evolution_dir / "memory" / "session_learnings.md"
    if memory_file.exists():
        try:
            content = memory_file.read_text(encoding="utf-8", errors="replace")
            result["memory_entries"] = len(re.findall(r"^###\s", content, re.MULTILINE))
        except Exception:
            pass

    return result


def scan_workspace(workspace_dir: Path) -> dict:
    """
    扫描当前工作区的项目层内容，返回摘要字典：
      project_context: exists|missing
      rules: [{name, source, description}, ...]
      skills: [{name, source, description}, ...]
    """
    result = {"project_context": "missing", "rules": [], "skills": []}

    project_context = workspace_dir / "project_context.md"
    if project_context.exists():
        result["project_context"] = "exists"

    for root_name in (".agents", ".cursor"):
        rules_dir = workspace_dir / root_name / "rules"
        if rules_dir.exists():
            for f in sorted(rules_dir.glob("*.mdc")):
                result["rules"].append({
                    "name": f.name,
                    "source": f"{root_name}/rules",
                    "description": _read_description(f),
                })

        skills_dir = workspace_dir / root_name / "skills"
        if skills_dir.exists():
            for d in sorted(skills_dir.iterdir()):
                if d.is_dir() and not d.name.startswith("."):
                    skill_md = d / "SKILL.md"
                    desc = _read_description(skill_md) if skill_md.exists() else "(无 SKILL.md)"
                    result["skills"].append({
                        "name": d.name,
                        "source": f"{root_name}/skills",
                        "description": desc,
                    })

    return result


# ─────────────────────────────────────────────────────────────
# 输出
# ─────────────────────────────────────────────────────────────

def print_result(
    init_status: str,
    evolution_dir: Path,
    scan: dict,
    workspace_dir: Path = None,
    workspace_scan: dict = None,
) -> None:
    """输出结构化报告到 stdout，AI 可直接读取做决策。"""
    lines = []
    lines.append(f"[INIT_STATUS] {init_status}")
    lines.append(f"[EVOLUTION_PATH] {evolution_dir}")
    lines.append(f"[TEMPLATES_DIR] {_TEMPLATES_DIR}")
    if workspace_dir is not None:
        lines.append(f"[WORKSPACE_PATH] {workspace_dir}")
        project_context = workspace_scan["project_context"] if workspace_scan else "missing"
        lines.append(f"[PROJECT_CONTEXT] {project_context}")

    lines.append("[EXISTING_RULES]")
    if scan["rules"]:
        for r in scan["rules"]:
            lines.append(f"  - {r['name']}: {r['description']}")
    else:
        lines.append("  (空)")

    if workspace_dir is not None:
        lines.append("[EXISTING_PROJECT_RULES]")
        if workspace_scan and workspace_scan["rules"]:
            for r in workspace_scan["rules"]:
                lines.append(f"  - {r['source']}/{r['name']}: {r['description']}")
        else:
            lines.append("  (空)")

    lines.append("[EXISTING_SKILLS]")
    if scan["skills"]:
        for s in scan["skills"]:
            lines.append(f"  - {s['name']}: {s['description']}")
    else:
        lines.append("  (空)")

    if workspace_dir is not None:
        lines.append("[EXISTING_PROJECT_SKILLS]")
        if workspace_scan and workspace_scan["skills"]:
            for s in workspace_scan["skills"]:
                lines.append(f"  - {s['source']}/{s['name']}: {s['description']}")
        else:
            lines.append("  (空)")

    lines.append(f"[EXISTING_MEMORY_ENTRIES] {scan['memory_entries']}")

    has_project_existing = bool(
        workspace_scan
        and (
            workspace_scan["project_context"] == "exists"
            or workspace_scan["rules"]
            or workspace_scan["skills"]
        )
    )
    has_existing = bool(scan["rules"] or scan["skills"])
    if workspace_dir is not None and has_project_existing:
        lines.append(
            "[AI_HINT] 当前已存在项目层锚点，请先判断本次经验是否只在当前项目成立；"
            "若是，优先读取 project_context/.agents，并兼容旧 .cursor；新增写入默认 .agents，避免误写入 puppet-vault。"
        )
    elif workspace_dir is not None:
        lines.append(
            "[AI_HINT] 已提供工作区，请先做“项目层 / 全局层”分层判断；"
            "仅当经验脱离当前项目后仍成立时，才写入 puppet-vault。"
        )
    elif has_existing:
        lines.append(
            "[AI_HINT] 发现现有内容，请先逐条对比当前需求与已有 Rule/Skill 的 description，"
            "判断是否有高度相似项可以迭代（patch），避免重复创建。"
            "相似度判断标准：触发场景一致、约束域重叠 > 50%。"
        )
    else:
        lines.append("[AI_HINT] puppet-vault 内容为空，直接创建新的 Rule/Skill。")

    out = "\n".join(lines)
    try:
        sys.stdout.buffer.write(out.encode("utf-8"))
        sys.stdout.buffer.write(b"\n")
        sys.stdout.buffer.flush()
    except AttributeError:
        print(out)


# ─────────────────────────────────────────────────────────────
# 入口
# ─────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="puppet-self-evolve: puppet-vault 初始化检查 + 分层内容扫描"
    )
    parser.add_argument(
        "--agents-home",
        default=None,
        help="当前 Agent home；Codex/Claude/Gemini 推荐使用该参数或 AGENTS_HOME 环境变量",
    )
    parser.add_argument(
        "--cursor-home",
        default=None,
        help="Cursor home 目录（历史兼容；未传 AGENTS_HOME 时使用）",
    )
    parser.add_argument(
        "--evolution-home",
        default=None,
        help="显式指定 puppet-vault 运行态目录；优先级高于 AGENTS_HOME/CURSOR_HOME",
    )
    parser.add_argument(
        "--workspace",
        default=None,
        help="当前项目根目录；提供后同步扫描项目层（project_context/.agents，兼容旧 .cursor）",
    )
    args = parser.parse_args()

    if args.agents_home:
        agents_home = Path(args.agents_home).expanduser()
    elif args.cursor_home:
        agents_home = Path(args.cursor_home).expanduser()
    else:
        agents_home = get_agents_home()
    evolution_dir = get_evolution_dir(agents_home, args.evolution_home or "")
    workspace_dir = Path(args.workspace) if args.workspace else None

    init_status = ensure_evolution_plugin(evolution_dir)
    scan = scan_evolution(evolution_dir)
    workspace_scan = scan_workspace(workspace_dir) if workspace_dir else None
    print_result(init_status, evolution_dir, scan, workspace_dir, workspace_scan)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
