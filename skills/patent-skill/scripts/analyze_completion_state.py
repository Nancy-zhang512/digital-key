from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from openpyxl import load_workbook


PLACEHOLDER_VALUES = {
    "",
    "-",
    "--",
    "/",
    "n/a",
    "na",
    "none",
    "null",
    "详见链接",
    "见链接",
    "待补充",
    "待完善",
}


HEADER_ALIASES = {
    "patent_no": ["公开(公告)号", "专利号", "公开号"],
    "independent_claim": ["独立权利要求(译)(简体中文)", "独立权利要求", "第一权利要求"],
    "technical_problem": ["技术问题"],
    "technical_solution": ["技术手段"],
    "technical_effect": ["技术功效"],
}


@dataclass(frozen=True)
class ColumnMap:
    patent_no: int
    independent_claim: int
    technical_problem: int
    technical_solution: int
    technical_effect: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze a patent completion workbook and write a resumable state snapshot."
    )
    parser.add_argument("xlsx_path", help="Path to the local workbook exported from Feishu.")
    parser.add_argument(
        "--output",
        help="Output JSON path. Defaults to tmp*/run_state/<workbook>.analysis.json",
    )
    parser.add_argument(
        "--progress-output",
        help="Optional progress JSON path. Defaults to tmp*/run_state/<workbook>.progress.json",
    )
    return parser.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def normalize_text(value: object) -> str:
    if value is None:
        return ""
    text = str(value).replace("_x000D_", "\n").strip()
    return text


def is_placeholder(text: str) -> bool:
    lowered = text.strip().lower()
    return lowered in PLACEHOLDER_VALUES


def looks_non_chinese(text: str) -> bool:
    if not text:
        return False
    chinese_chars = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    latin_chars = sum(1 for ch in text if ch.isascii() and ch.isalpha())
    return chinese_chars == 0 and latin_chars >= 12


def classify_field(text: str, *, claim: bool = False) -> str:
    if not text or is_placeholder(text):
        return "missing"
    if claim and looks_non_chinese(text):
        return "needs_translation"
    return "complete"


def find_column(headers: list[str], candidates: Iterable[str]) -> int:
    for candidate in candidates:
        for index, header in enumerate(headers, start=1):
            if header == candidate:
                return index
    raise ValueError(f"missing required header from {list(candidates)}")


def build_column_map(headers: list[str]) -> ColumnMap:
    return ColumnMap(
        patent_no=find_column(headers, HEADER_ALIASES["patent_no"]),
        independent_claim=find_column(headers, HEADER_ALIASES["independent_claim"]),
        technical_problem=find_column(headers, HEADER_ALIASES["technical_problem"]),
        technical_solution=find_column(headers, HEADER_ALIASES["technical_solution"]),
        technical_effect=find_column(headers, HEADER_ALIASES["technical_effect"]),
    )


def default_output_path(xlsx_path: Path) -> Path:
    run_state_dir = xlsx_path.parent / "run_state"
    return run_state_dir / f"{xlsx_path.stem}.analysis.json"


def default_progress_path(xlsx_path: Path) -> Path:
    run_state_dir = xlsx_path.parent / "run_state"
    return run_state_dir / f"{xlsx_path.stem}.progress.json"


def row_status(field_states: dict[str, str], has_link: bool) -> str:
    if not has_link:
        return "blocked"
    if any(state != "complete" for state in field_states.values()):
        return "pending"
    return "done"


def main() -> int:
    args = parse_args()
    xlsx_path = Path(args.xlsx_path).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve() if args.output else default_output_path(xlsx_path)
    progress_path = (
        Path(args.progress_output).expanduser().resolve()
        if args.progress_output
        else default_progress_path(xlsx_path)
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    progress_path.parent.mkdir(parents=True, exist_ok=True)

    workbook = load_workbook(xlsx_path, read_only=False, data_only=False)
    sheet = workbook[workbook.sheetnames[0]]
    headers = [normalize_text(sheet.cell(row=1, column=index).value) for index in range(1, sheet.max_column + 1)]
    columns = build_column_map(headers)

    rows: list[dict[str, object]] = []
    counter: Counter[str] = Counter()
    for row_index in range(2, sheet.max_row + 1):
        patent_cell = sheet.cell(row=row_index, column=columns.patent_no)
        patent_no = normalize_text(patent_cell.value)
        hyperlink = getattr(patent_cell.hyperlink, "target", None)
        if not patent_no and not hyperlink:
            continue

        field_values = {
            "independent_claim": normalize_text(sheet.cell(row=row_index, column=columns.independent_claim).value),
            "technical_problem": normalize_text(sheet.cell(row=row_index, column=columns.technical_problem).value),
            "technical_solution": normalize_text(sheet.cell(row=row_index, column=columns.technical_solution).value),
            "technical_effect": normalize_text(sheet.cell(row=row_index, column=columns.technical_effect).value),
        }
        field_states = {
            "independent_claim": classify_field(field_values["independent_claim"], claim=True),
            "technical_problem": classify_field(field_values["technical_problem"]),
            "technical_solution": classify_field(field_values["technical_solution"]),
            "technical_effect": classify_field(field_values["technical_effect"]),
        }
        status = row_status(field_states, bool(hyperlink))
        counter[status] += 1
        rows.append(
            {
                "row": row_index,
                "patent_no": patent_no,
                "hyperlink": hyperlink,
                "status": status,
                "field_states": field_states,
                "blocked_reason": "" if hyperlink else "缺少智慧芽超链接",
                "local_excel_write": "not_started",
                "feishu_sheet_sync": "not_started",
                "updated_fields": [],
                "updated_at": None,
            }
        )

    generated_at = utc_now()
    payload = {
        "generated_at": generated_at,
        "source_workbook": str(xlsx_path),
        "sheet_name": sheet.title,
        "summary": {
            "total_rows": len(rows),
            "done": counter["done"],
            "pending": counter["pending"],
            "blocked": counter["blocked"],
        },
        "columns": {
            "patent_no": columns.patent_no,
            "independent_claim": columns.independent_claim,
            "technical_problem": columns.technical_problem,
            "technical_solution": columns.technical_solution,
            "technical_effect": columns.technical_effect,
        },
        "rows": rows,
    }

    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    progress_payload = {
        "generated_at": generated_at,
        "source_workbook": str(xlsx_path),
        "sheet_name": sheet.title,
        "summary": {
            "total_rows": len(rows),
            "done": counter["done"],
            "pending": counter["pending"],
            "blocked": counter["blocked"],
            "remote_pending": 0,
            "in_progress": 0,
        },
        "rows": [
            {
                **row,
                "local_excel_write": "success",
                "feishu_sheet_sync": "not_started",
                "updated_at": generated_at,
            }
            for row in rows
        ],
        "last_updated_at": generated_at,
    }
    progress_path.write_text(json.dumps(progress_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(str(output_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
