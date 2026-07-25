# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def vault_root() -> Path:
    return Path(__file__).resolve().parents[3]


def pool_path() -> Path:
    return vault_root() / "memory" / "candidate_pool.jsonl"


def today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def load_items() -> List[Dict[str, Any]]:
    path = pool_path()
    if not path.exists():
        return []
    items = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            items.append(json.loads(line))
    return items


def save_items(items: List[Dict[str, Any]]) -> None:
    path = pool_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(item, ensure_ascii=False, sort_keys=True) for item in items]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def make_id(name: str) -> str:
    digest = hashlib.sha1(f"{today()}:{name}".encode("utf-8")).hexdigest()[:8]
    return f"{today()}-{digest}"


def find_item(items: List[Dict[str, Any]], key: str) -> Optional[Dict[str, Any]]:
    lowered = key.casefold()
    for item in items:
        if item.get("id") == key or str(item.get("name", "")).casefold() == lowered:
            return item
    return None


def print_json(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_check(args: argparse.Namespace) -> int:
    item = find_item(load_items(), args.name)
    print_json({"found": bool(item), "item": item})
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    items = load_items()
    item = find_item(items, args.name)
    if item:
        print_json({"status": "exists", "item": item})
        return 0
    now = today()
    item = {
        "id": make_id(args.name),
        "name": args.name,
        "type": "GlobalCandidate",
        "trigger_count": 1,
        "maturity": "candidate",
        "rule": args.rule,
        "evidence": [{"summary": args.evidence}],
        "created_at": now,
        "updated_at": now,
    }
    items.append(item)
    save_items(items)
    print_json({"status": "added", "item": item})
    return 0


def parse_delta(value: str) -> int:
    if value.startswith("+"):
        return int(value[1:])
    return int(value)


def cmd_update(args: argparse.Namespace) -> int:
    items = load_items()
    item = find_item(items, args.id)
    if not item:
        print_json({"status": "missing", "id": args.id})
        return 1
    if item.get("maturity") == "rejected":
        print_json({"status": "rejected", "item": item})
        return 0
    item["trigger_count"] = int(item.get("trigger_count", 0)) + parse_delta(args.trigger_count)
    if args.add_evidence:
        item.setdefault("evidence", []).append({"summary": args.add_evidence})
    item["updated_at"] = today()
    save_items(items)
    print_json({"status": "updated", "item": item})
    return 0


def cmd_mark(args: argparse.Namespace, maturity: str) -> int:
    items = load_items()
    item = find_item(items, args.id)
    if not item:
        print_json({"status": "missing", "id": args.id})
        return 1
    item["maturity"] = maturity
    item["updated_at"] = today()
    save_items(items)
    print_json({"status": maturity, "item": item})
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    items = load_items()
    if args.maturity:
        items = [item for item in items if item.get("maturity") == args.maturity]
    print_json({"items": items})
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="管理 puppet-vault 全局候选池")
    sub = parser.add_subparsers(dest="action", required=True)
    check = sub.add_parser("check")
    check.add_argument("name")
    add = sub.add_parser("add")
    add.add_argument("--name", required=True)
    add.add_argument("--rule", required=True)
    add.add_argument("--evidence", required=True)
    update = sub.add_parser("update")
    update.add_argument("id")
    update.add_argument("--trigger-count", default="+1")
    update.add_argument("--add-evidence", default="")
    mature = sub.add_parser("mature")
    mature.add_argument("id")
    reject = sub.add_parser("reject")
    reject.add_argument("id")
    list_cmd = sub.add_parser("list")
    list_cmd.add_argument("--maturity", choices=["candidate", "mature", "rejected"])
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.action == "check":
        return cmd_check(args)
    if args.action == "add":
        return cmd_add(args)
    if args.action == "update":
        return cmd_update(args)
    if args.action == "mature":
        return cmd_mark(args, "mature")
    if args.action == "reject":
        return cmd_mark(args, "rejected")
    if args.action == "list":
        return cmd_list(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
