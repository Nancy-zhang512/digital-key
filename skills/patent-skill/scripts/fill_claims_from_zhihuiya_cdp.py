from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import time
import urllib.parse
import urllib.request
from urllib.error import HTTPError
from pathlib import Path

from openpyxl import load_workbook


PLACEHOLDERS = {"", "-", "--", "/", "n/a", "na", "none", "null", "详见链接", "见链接", "待补充", "待完善"}


def post(url: str, data: str) -> dict:
    request = urllib.request.Request(url, data=data.encode("utf-8"), method="POST")
    last_error: Exception | None = None
    for _ in range(8):
        try:
            with urllib.request.urlopen(request) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            last_error = error
            if error.code != 500:
                raise
            time.sleep(1)
    if last_error:
        raise last_error
    raise RuntimeError(f"request failed: {url}")


def get(url: str) -> dict:
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read().decode("utf-8"))


def normalize_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).replace("_x000D_", "\n").strip()


def build_claims_url(hyperlink: str) -> str:
    return hyperlink.replace("/patent-view/abst?", "/patent-view/clms?")


def extract_first_claim(claim_text: str) -> str:
    text = claim_text.replace("\r", "").strip()
    match = re.search(
        r"((?:\[\s*1\s*\]|\[\s*Revendication\s*1\s*\]|1\.|Anspruch\s*1|Claim\s*1)[\s\S]*?)(?=\n(?:\[\s*\d+\s*\]|\[\s*Revendication\s*\d+\s*\]|\d+\.|Anspruch\s*\d+|Claim\s*\d+)|\Z)",
        text,
        flags=re.S | re.I,
    )
    if not match:
        raise ValueError("failed to locate first original claim block")
    claim = re.sub(r"\s+\n", "\n", match.group(1)).strip()
    return claim


def update_progress(
    progress_path: Path,
    *,
    row_number: int,
    claim_done: bool,
    local_excel_write: str,
    feishu_sheet_sync: str,
    blocked_reason: str = "",
) -> None:
    payload = json.loads(progress_path.read_text(encoding="utf-8"))
    row = next(item for item in payload["rows"] if item["row"] == row_number)
    row.setdefault("field_states", {})
    if claim_done:
        row["field_states"]["independent_claim"] = "complete"
    remaining = [state for state in row["field_states"].values() if state != "complete"]
    row["status"] = "done" if not remaining else "pending"
    row["local_excel_write"] = local_excel_write
    row["feishu_sheet_sync"] = feishu_sheet_sync
    row["blocked_reason"] = blocked_reason
    updated_fields = set(row.get("updated_fields", []))
    if claim_done:
        updated_fields.add("independent_claim")
    row["updated_fields"] = sorted(updated_fields)
    row["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")

    summary = {"total_rows": len(payload["rows"]), "done": 0, "pending": 0, "blocked": 0, "remote_pending": 0, "in_progress": 0}
    for item in payload["rows"]:
        summary[item["status"]] = summary.get(item["status"], 0) + 1
    payload["summary"] = summary
    payload["last_updated_at"] = row["updated_at"]
    progress_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def csv_single_cell(value: str) -> str:
    from io import StringIO

    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow([value])
    return buffer.getvalue()


def sync_single_cell(sheet_url: str, sheet_name: str, row_number: int, value: str) -> None:
    csv_text = csv_single_cell(value)
    command = [
        "lark-cli",
        "sheets",
        "+csv-put",
        "--url",
        sheet_url,
        "--sheet-name",
        sheet_name,
        "--start-cell",
        f"E{row_number}",
        "--csv",
        "-",
    ]
    subprocess.run(command, input=csv_text.encode("utf-8"), check=True)


def eval_js(target_id: str, expression: str) -> str:
    result = post(f"http://localhost:3456/eval?target={urllib.parse.quote(target_id)}", expression)
    value = result.get("value")
    if not isinstance(value, str):
        raise ValueError(f"unexpected eval result: {result}")
    return value


def ensure_original_and_read_claims(target_id: str) -> str:
    expression = r"""
(async () => {
  const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
  const click = selector => {
    const element = document.querySelector(selector);
    if (element) {
      element.click();
      return true;
    }
    return false;
  };
  const current = document.querySelector('.translate-dropdown-title')?.innerText?.trim();
  if (current !== '原文') {
    click('a.el-tooltip.elstc-btn');
    await sleep(250);
    click('li.pendo-track__function-bar__translate-NON');
  }
  for (let i = 0; i < 30; i++) {
    const block = document.querySelector('#clms-render__clms-container .pt-section__body, #clms-render__clms-container');
    if (block && block.innerText && block.innerText.length > 50) {
      return block.innerText;
    }
    await sleep(500);
  }
  return '';
})()
"""
    return eval_js(target_id, expression)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fill translated independent claims from Zhihuiya's rendered CN block.")
    parser.add_argument("--workbook", required=True)
    parser.add_argument("--progress", required=True)
    parser.add_argument("--sheet-url", required=True)
    parser.add_argument("--sheet-name", required=True)
    parser.add_argument("--rows", help="Comma-separated Excel row numbers to process.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    workbook_path = Path(args.workbook).expanduser().resolve()
    progress_path = Path(args.progress).expanduser().resolve()
    requested_rows = {int(item) for item in args.rows.split(",")} if args.rows else None

    progress = json.loads(progress_path.read_text(encoding="utf-8"))
    rows = [row for row in progress["rows"] if row["status"] == "pending"]
    if requested_rows is not None:
        rows = [row for row in rows if row["row"] in requested_rows]

    for row in rows:
        row_number = row["row"]
        try:
            workbook = load_workbook(workbook_path)
            sheet = workbook[workbook.sheetnames[0]]
            existing_claim = normalize_text(sheet[f"E{row_number}"].value)
            claim_state = row.get("field_states", {}).get("independent_claim")
            if claim_state == "complete" and existing_claim.lower() not in PLACEHOLDERS:
                continue
            hyperlink = row.get("hyperlink") or getattr(sheet[f"B{row_number}"].hyperlink, "target", None)
            if not hyperlink:
                update_progress(progress_path, row_number=row_number, claim_done=False, local_excel_write="failed", feishu_sheet_sync="failed", blocked_reason="缺少智慧芽超链接")
                continue

            claims_url = build_claims_url(hyperlink)
            target_id = post("http://localhost:3456/new", claims_url)["targetId"]
            time.sleep(2)

            translated_block = ensure_original_and_read_claims(target_id)
            get(f"http://localhost:3456/close?target={urllib.parse.quote(target_id)}")
            if not translated_block:
                update_progress(progress_path, row_number=row_number, claim_done=False, local_excel_write="failed", feishu_sheet_sync="failed", blocked_reason="未读取到智慧芽原文权利要求")
                continue

            claim = extract_first_claim(translated_block)
            sheet[f"E{row_number}"] = claim
            workbook.save(workbook_path)

            try:
                sync_single_cell(args.sheet_url, args.sheet_name, row_number, claim)
            except subprocess.CalledProcessError as error:
                update_progress(progress_path, row_number=row_number, claim_done=True, local_excel_write="success", feishu_sheet_sync="failed", blocked_reason=f"飞书同步失败: {error}")
                continue

            update_progress(progress_path, row_number=row_number, claim_done=True, local_excel_write="success", feishu_sheet_sync="success")
            print(f"updated row {row_number}")
        except Exception as error:
            update_progress(progress_path, row_number=row_number, claim_done=False, local_excel_write="failed", feishu_sheet_sync="failed", blocked_reason=f"处理失败: {error}")
            print(f"failed row {row_number}: {error}")
            continue

    final_path = workbook_path.with_name(f"{workbook_path.stem}_补全结果{workbook_path.suffix}")
    final_workbook = load_workbook(workbook_path)
    final_workbook.save(final_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
