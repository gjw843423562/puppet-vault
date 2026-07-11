# -*- coding: utf-8 -*-
"""
puppet-vault 个人规则库 Git 同步脚本。

用法：
  python puppet_sync.py init
  python puppet_sync.py pull [--force]
  python puppet_sync.py push
  python puppet_sync.py commit [--message MSG]
  python puppet_sync.py status
  python puppet_sync.py daily-pull [--quiet]
  python puppet_sync.py session-end
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("PYTHONUTF8", "1")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_REMOTE = "https://github.com/gjw843423562/puppet-vault.git"
DEFAULT_BRANCH = "main"
TZ_OFFSET = timezone(timedelta(hours=8))


def _cursor_home() -> Path:
    env = os.environ.get("CURSOR_HOME")
    if env:
        p = Path(env)
        if p.name.lower() != ".cursor":
            p = p / ".cursor"
        return p.resolve()
    return (Path(os.environ.get("USERPROFILE", Path.home())) / ".cursor").resolve()


def _vault_root() -> Path:
    return _cursor_home() / "plugins" / "local" / "puppet-vault"


def _sync_state_path() -> Path:
    return _cursor_home() / "local_data" / "puppet-vault" / "sync_state.json"


def _sync_log_path() -> Path:
    return _cursor_home() / "logs" / "puppet_vault_sync.jsonl"


def _run_git(args: List[str], cwd: Path) -> Tuple[int, str, str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.returncode, (proc.stdout or "").strip(), (proc.stderr or "").strip()


def _append_log(record: Dict[str, Any]) -> None:
    path = _sync_log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    record["ts"] = datetime.now(TZ_OFFSET).isoformat(timespec="seconds")
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _load_sync_state() -> Dict[str, Any]:
    path = _sync_state_path()
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_sync_state(state: Dict[str, Any]) -> None:
    path = _sync_state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def _today_str() -> str:
    return datetime.now(TZ_OFFSET).strftime("%Y-%m-%d")


def _git_head(cwd: Path) -> str:
    code, out, _ = _run_git(["rev-parse", "--short", "HEAD"], cwd)
    return out if code == 0 else ""


def _has_remote(cwd: Path) -> bool:
    code, out, _ = _run_git(["remote"], cwd)
    return code == 0 and bool(out.strip())


def _is_dirty(cwd: Path) -> bool:
    code, out, _ = _run_git(["status", "--porcelain"], cwd)
    return code == 0 and bool(out.strip())


def _ensure_git_repo(cwd: Path) -> Tuple[bool, str]:
    if (cwd / ".git").exists():
        return True, "already_exists"
    code, _, err = _run_git(["init", "-b", DEFAULT_BRANCH], cwd)
    if code != 0:
        return False, err or "git init failed"
    return True, "created"


def _ensure_remote(cwd: Path, remote_url: str) -> Tuple[bool, str]:
    if not _has_remote(cwd):
        code, _, err = _run_git(["remote", "add", "origin", remote_url], cwd)
        if code != 0:
            return False, err or "remote add failed"
        return True, "remote_added"
    code, out, _ = _run_git(["remote", "get-url", "origin"], cwd)
    if remote_url not in (out or ""):
        code, _, err = _run_git(["remote", "set-url", "origin", remote_url], cwd)
        if code != 0:
            return False, err or "remote set-url failed"
        return True, "remote_updated"
    return True, "remote_ok"


def _ensure_git_identity(cwd: Path) -> None:
    """仅在本仓库设置提交者身份，不修改全局 git config。"""
    code, name, _ = _run_git(["config", "user.name"], cwd)
    if code != 0 or not name.strip():
        _run_git(["config", "user.name", "gjw843423562"], cwd)
    code, email, _ = _run_git(["config", "user.email"], cwd)
    if code != 0 or not email.strip():
        _run_git(
            ["config", "user.email", "gjw843423562@users.noreply.github.com"],
            cwd,
        )


def cmd_init(remote_url: str) -> int:
    root = _vault_root()
    if not root.is_dir():
        print(f"[ERROR] puppet-vault 目录不存在: {root}")
        return 1
    ok, msg = _ensure_git_repo(root)
    if not ok:
        print(f"[ERROR] {msg}")
        return 1
    _ensure_git_identity(root)
    ok, remote_msg = _ensure_remote(root, remote_url)
    if not ok:
        print(f"[ERROR] {remote_msg}")
        return 1
    state = _load_sync_state()
    state.update({
        "remote": remote_url,
        "default_branch": DEFAULT_BRANCH,
        "initialized_at": datetime.now(TZ_OFFSET).isoformat(timespec="seconds"),
        "local_head": _git_head(root),
    })
    _save_sync_state(state)
    print(f"[INIT_OK] git={msg} remote={remote_msg}")
    print(f"[VAULT_ROOT] {root}")
    _append_log({"action": "init", "status": "ok", "remote": remote_url})
    return 0


def cmd_pull(force: bool = False, quiet: bool = False) -> int:
    root = _vault_root()
    if not (root / ".git").exists():
        if not quiet:
            print("[WARN] 未初始化 Git，跳过 pull")
        return 0
    if not _has_remote(root):
        if not quiet:
            print("[WARN] 未配置 remote，跳过 pull")
        return 0

    old_head = _git_head(root)
    fetch_code, _, fetch_err = _run_git(["fetch", "origin", DEFAULT_BRANCH], root)
    if fetch_code != 0:
        if not quiet:
            print(f"[WARN] fetch 失败: {fetch_err}")
        _append_log({"action": "pull", "status": "fetch_failed", "error": fetch_err})
        return 1

    if _is_dirty(root) and not force:
        if not quiet:
            print("[WARN] 本地有未提交改动，跳过 pull（可用 --force）")
        _append_log({"action": "pull", "status": "skipped_dirty"})
        return 0

    pull_code, pull_out, pull_err = _run_git(
        ["pull", "--ff-only", "origin", DEFAULT_BRANCH], root
    )
    new_head = _git_head(root)
    state = _load_sync_state()
    state["last_pull_date"] = _today_str()
    state["last_pull_at"] = datetime.now(TZ_OFFSET).isoformat(timespec="seconds")
    state["local_head"] = new_head
    state["remote_head"] = new_head
    _save_sync_state(state)

    if pull_code != 0:
        if not quiet:
            print(f"[WARN] pull 失败: {pull_err or pull_out}")
        _append_log({"action": "pull", "status": "failed", "error": pull_err})
        return 1

    if not quiet:
        if old_head and new_head and old_head != new_head:
            print(f"[PULL_OK] {old_head} -> {new_head}")
        else:
            print(f"[PULL_OK] 已是最新 ({new_head or 'no-commit'})")
    _append_log({"action": "pull", "status": "ok", "old": old_head, "new": new_head})
    return 0


def cmd_daily_pull(quiet: bool = False) -> Tuple[int, str]:
    state = _load_sync_state()
    today = _today_str()
    if state.get("last_pull_date") == today:
        msg = f"[puppet-vault] 今日已同步 ({state.get('local_head', 'unknown')})"
        return 0, msg
    code = cmd_pull(force=False, quiet=quiet)
    state = _load_sync_state()
    head = state.get("local_head", "unknown")
    if code == 0:
        return 0, f"[puppet-vault] 已自动拉取更新 (HEAD={head})"
    return code, f"[WARN: puppet-vault 同步失败，使用本地缓存 HEAD={head}]"


def cmd_commit(message: Optional[str] = None) -> int:
    root = _vault_root()
    if not (root / ".git").exists():
        print("[WARN] 未初始化 Git，跳过 commit")
        return 0
    if not _is_dirty(root):
        print("[STATUS] 工作区干净，无需提交")
        return 0

    _run_git(["add", "-A"], root)
    if not message:
        message = f"chore(sync): 自动同步 puppet-vault {_today_str()}"
    commit_code, _, commit_err = _run_git(["commit", "-m", message], root)
    if commit_code != 0:
        print(f"[ERROR] commit 失败: {commit_err}")
        _append_log({"action": "commit", "status": "failed", "error": commit_err})
        return 1

    head = _git_head(root)
    state = _load_sync_state()
    state["local_head"] = head
    state["last_commit_at"] = datetime.now(TZ_OFFSET).isoformat(timespec="seconds")
    state["local_dirty"] = False
    _save_sync_state(state)
    print(f"[COMMIT_OK] {head} {message}")
    _append_log({"action": "commit", "status": "ok", "head": head, "message": message})
    return 0


def cmd_push() -> int:
    root = _vault_root()
    if not (root / ".git").exists() or not _has_remote(root):
        print("[WARN] 未配置 Git/remote，跳过 push")
        return 0

    push_code, push_out, push_err = _run_git(
        ["push", "-u", "origin", DEFAULT_BRANCH], root
    )
    head = _git_head(root)
    state = _load_sync_state()
    state["remote_head"] = head
    state["last_push_at"] = datetime.now(TZ_OFFSET).isoformat(timespec="seconds")
    _save_sync_state(state)

    if push_code != 0:
        print(f"[ERROR] push 失败: {push_err or push_out}")
        _append_log({"action": "push", "status": "failed", "error": push_err})
        return 1

    print(f"[PUSH_OK] origin/{DEFAULT_BRANCH} ({head})")
    _append_log({"action": "push", "status": "ok", "head": head})
    return 0


def cmd_session_end() -> int:
    root = _vault_root()
    if not (root / ".git").exists():
        return 0
    if not _is_dirty(root):
        return 0
    if cmd_commit() != 0:
        return 1
    return cmd_push()


def cmd_status() -> int:
    root = _vault_root()
    state = _load_sync_state()
    print(f"[VAULT_ROOT] {root}")
    print(f"[GIT_REPO] {(root / '.git').exists()}")
    print(f"[REMOTE] {state.get('remote', DEFAULT_REMOTE)}")
    print(f"[LOCAL_HEAD] {_git_head(root) or state.get('local_head', '')}")
    print(f"[DIRTY] {_is_dirty(root)}")
    print(f"[LAST_PULL_DATE] {state.get('last_pull_date', 'never')}")
    print(f"[LAST_PUSH_AT] {state.get('last_push_at', 'never')}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="puppet-vault Git 同步")
    parser.add_argument(
        "action",
        choices=["init", "pull", "push", "commit", "status", "daily-pull", "session-end"],
    )
    parser.add_argument("--force", action="store_true", help="pull 时忽略本地脏改动")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--message", default=None)
    parser.add_argument("--remote", default=DEFAULT_REMOTE)
    args = parser.parse_args()

    actions = {
        "init": lambda: cmd_init(args.remote),
        "pull": lambda: cmd_pull(force=args.force, quiet=args.quiet),
        "push": cmd_push,
        "commit": lambda: cmd_commit(args.message),
        "status": cmd_status,
        "daily-pull": lambda: cmd_daily_pull(args.quiet)[0],
        "session-end": cmd_session_end,
    }
    return int(actions[args.action]() or 0)


if __name__ == "__main__":
    raise SystemExit(main())
