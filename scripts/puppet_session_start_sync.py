# -*- coding: utf-8 -*-
"""
sessionStart Hook：puppet-vault 日级自动拉取，并向会话注入同步结果。
输出 JSON：{"additional_context": "..."}
"""
import json
import os
import subprocess
import sys
from pathlib import Path

os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"


def _cursor_home() -> Path:
    env = os.environ.get("CURSOR_HOME")
    if env:
        p = Path(env)
        if p.name.lower() != ".cursor":
            p = p / ".cursor"
        return p.resolve()
    return (Path(os.environ.get("USERPROFILE", Path.home())) / ".cursor").resolve()


def _sync_script() -> Path:
    return (
        _cursor_home()
        / "plugins"
        / "local"
        / "puppet-vault"
        / "skills"
        / "puppet-vault-sync"
        / "scripts"
        / "puppet_sync.py"
    )


def _write_output(payload: dict) -> None:
    text = json.dumps(payload, ensure_ascii=False)
    try:
        if hasattr(sys.stdout, "buffer") and sys.stdout.buffer:
            sys.stdout.buffer.write(text.encode("utf-8"))
            sys.stdout.buffer.flush()
            return
    except Exception:
        pass
    sys.stdout.write(text)
    sys.stdout.flush()


def main() -> int:
    script = _sync_script()
    if not script.is_file():
        _write_output({
            "additional_context": "[WARN: puppet-vault 同步脚本缺失，跳过日级拉取]"
        })
        return 0

    proc = subprocess.run(
        [sys.executable, str(script), "daily-pull", "--quiet"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    msg = (proc.stdout or "").strip() or "[puppet-vault] 同步检查完成"
    if proc.returncode != 0:
        err = (proc.stderr or "").strip()
        if err:
            msg = f"{msg}\n{err}"
    _write_output({"additional_context": msg})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
