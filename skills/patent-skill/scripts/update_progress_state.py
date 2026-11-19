from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ALLOWED_STATUS = {"pending", "in_progress", "done", "blocked", "remote_pending"}
ALLOWED_WRITE_STATE = {"not_started", "pending", "success", "failed"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update one row in a patent completion progress file.")
    parser.add_argument("state_path", help="Path to the progress JSON file.")
    parser.add_argument("--row", type=int, required=True, help="Excel row number to update.")
    parser.add_argument("--patent-no", help="Patent number for the row.")
    parser.add_argument("--status", choices=sorted(ALLOWED_STATUS), required=True)
    parser.add_argument(
        "--local-excel-write",
        choices=sorted(ALLOWED_WRITE_STATE),
        help="Local Excel write state.",
    )
    parser.add_argument(
        "--feishu-sheet-sync",
        choices=sorted(ALLOWED_WRITE_STATE),
        help="Feishu sheet sync state.",
    )
    parser.add_argument(
        "--updated-fields",
        help="Comma-separated list of fields updated for this row.",
    )
    parser.add_argument("--blocked-reason", default="", help="Why the row is blocked or pending.")
    parser.add_argument("--hyperlink", help="Zhihuiya hyperlink for the row.")
    return parser.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_state(path: Path) -> dict:
    if not path.exists():
        return {
            "generated_at": utc_now(),
            "summary": {"total_rows": 0, "done": 0, "pending": 0, "blocked": 0, "remote_pending": 0, "in_progress": 0},
            "rows": [],
        }
    return json.loads(path.read_text(encoding="utf-8"))


def recompute_summary(rows: list[dict]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for row in rows:
        counter[row["status"]] += 1
    summary = {
        "total_rows": len(rows),
        "done": counter["done"],
        "pending": counter["pending"],
        "blocked": counter["blocked"],
        "remote_pending": counter["remote_pending"],
        "in_progress": counter["in_progress"],
    }
    return summary


def save_atomic(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp_path.replace(path)


def main() -> int:
    args = parse_args()
    state_path = Path(args.state_path).expanduser().resolve()
    state = load_state(state_path)
    rows = state.setdefault("rows", [])
    row_entry = next((row for row in rows if row.get("row") == args.row), None)
    if row_entry is None:
        row_entry = {
            "row": args.row,
            "patent_no": args.patent_no or "",
            "hyperlink": args.hyperlink,
            "field_states": {},
            "updated_fields": [],
            "local_excel_write": "not_started",
            "feishu_sheet_sync": "not_started",
            "blocked_reason": "",
        }
        rows.append(row_entry)

    if args.patent_no:
        row_entry["patent_no"] = args.patent_no
    if args.hyperlink:
        row_entry["hyperlink"] = args.hyperlink
    row_entry["status"] = args.status
    if args.local_excel_write:
        row_entry["local_excel_write"] = args.local_excel_write
    if args.feishu_sheet_sync:
        row_entry["feishu_sheet_sync"] = args.feishu_sheet_sync
    if args.updated_fields is not None:
        row_entry["updated_fields"] = [field.strip() for field in args.updated_fields.split(",") if field.strip()]
    row_entry["blocked_reason"] = args.blocked_reason
    row_entry["updated_at"] = utc_now()

    state["summary"] = recompute_summary(rows)
    state["last_updated_at"] = row_entry["updated_at"]
    save_atomic(state_path, state)
    print(str(state_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
