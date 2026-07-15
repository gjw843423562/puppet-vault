# -*- coding: utf-8 -*-
"""
安装 puppet-vault 的 Cursor/Codex 运行入口。

该脚本只创建目录入口，不复制规则或技能正文；正本始终保留在 vault_root。
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

DEFAULT_SKILLS = ("puppet-vault-skill", "puppet-vault-sync", "puppet-self-evolve")
CURSOR_ENTRIES = (".cursor-plugin", "references", "rules", "scripts", "skills", "sync")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def _user_home() -> Path:
    return Path(os.environ.get("USERPROFILE", Path.home())).absolute()


def _default_vault_root() -> Path:
    env = os.environ.get("PUPPET_VAULT_ROOT")
    if env:
        return Path(env).absolute()
    return Path(__file__).resolve().parents[1]


def _cursor_plugin_root() -> Path:
    env = os.environ.get("CURSOR_HOME")
    home = Path(env).absolute() if env else _user_home() / ".cursor"
    if home.name.lower() != ".cursor":
        home = home / ".cursor"
    return home / "plugins" / "local" / "puppet-vault"


def _codex_skills_root() -> Path:
    env = os.environ.get("AGENTS_HOME")
    home = Path(env).absolute() if env else _user_home() / ".codex"
    return home / "skills"


def _is_link_to(path: Path, target: Path) -> bool:
    if not path.exists():
        return False
    try:
        return path.resolve() == target.resolve()
    except OSError:
        return False


def _make_link(link: Path, target: Path, dry_run: bool) -> str:
    if _is_link_to(link, target):
        return f"OK 已存在: {link} -> {target}"
    if link.exists():
        return f"SKIP 已存在且非目标入口: {link}"
    if dry_run:
        return f"DRY-RUN 将创建: {link} -> {target}"
    link.parent.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        proc = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)])
        if proc.returncode != 0:
            return f"ERROR 创建失败: {link}"
    else:
        link.symlink_to(target, target_is_directory=True)
    return f"CREATED: {link} -> {target}"


def install_cursor(vault_root: Path, dry_run: bool) -> list[str]:
    root = _cursor_plugin_root()
    results = []
    if not dry_run:
        root.mkdir(parents=True, exist_ok=True)
    for name in CURSOR_ENTRIES:
        results.append(_make_link(root / name, vault_root / name, dry_run))
    return results


def install_codex(vault_root: Path, dry_run: bool) -> list[str]:
    root = _codex_skills_root()
    results = []
    for name in DEFAULT_SKILLS:
        results.append(_make_link(root / name, vault_root / "skills" / name, dry_run))
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="安装 puppet-vault 运行入口")
    parser.add_argument("--vault-root", default=str(_default_vault_root()))
    parser.add_argument("--agents", default="cursor,codex")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    vault_root = Path(args.vault_root).absolute()
    if not vault_root.is_dir():
        print(f"ERROR vault_root 不存在: {vault_root}")
        return 1
    selected = {item.strip().lower() for item in args.agents.split(",") if item.strip()}
    results = []
    if "cursor" in selected:
        results.extend(install_cursor(vault_root, args.dry_run))
    if "codex" in selected:
        results.extend(install_codex(vault_root, args.dry_run))
    for line in results:
        print(line)
    return 0 if not any(line.startswith("ERROR") for line in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
