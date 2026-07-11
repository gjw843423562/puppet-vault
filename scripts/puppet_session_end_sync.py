# -*- coding: utf-8 -*-
"""
sessionEnd Hook：puppet-vault 脏改动自动提交并推送。
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


def main() -> int:
    script = _sync_script()
    if not script.is_file():
        return 0
    subprocess.run(
        [sys.executable, str(script), "session-end"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
