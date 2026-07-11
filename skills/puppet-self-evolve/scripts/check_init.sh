#!/usr/bin/env sh
set -eu

# Wrapper for check_init.py with Python 3 resolution.

SCRIPT_DIR=$(CDPATH= cd "$(dirname "$0")" && pwd)
PY_SCRIPT="$SCRIPT_DIR/check_init.py"
RESOLVE_PY="$SCRIPT_DIR/../../../../sc-core/scripts/resolve_python.sh"
if [ ! -f "$RESOLVE_PY" ]; then
  RESOLVE_PY="$SCRIPT_DIR/../../../scripts/resolve_python.sh"
fi

export PYTHONIOENCODING=utf-8

if [ ! -f "$PY_SCRIPT" ]; then
  echo "[ERROR] Python helper script not found: $PY_SCRIPT" >&2
  exit 1
fi

if [ ! -f "$RESOLVE_PY" ]; then
  echo "[ERROR] resolve_python.sh not found: $RESOLVE_PY" >&2
  exit 1
fi

. "$RESOLVE_PY"

if [ -n "${SKILLS_PY_ARGS:-}" ]; then
  "$SKILLS_PY_CMD" $SKILLS_PY_ARGS "$PY_SCRIPT" "$@"
else
  "$SKILLS_PY_CMD" "$PY_SCRIPT" "$@"
fi
