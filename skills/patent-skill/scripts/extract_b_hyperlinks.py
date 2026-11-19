from __future__ import annotations

import json
import sys
from pathlib import Path

from openpyxl import load_workbook


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python3 extract_b_hyperlinks.py <xlsx-path>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1]).expanduser().resolve()
    wb = load_workbook(path, read_only=False)
    ws = wb[wb.sheetnames[0]]
    rows = []

    for row_idx in range(2, ws.max_row + 1):
        cell = ws[f"B{row_idx}"]
        patent_no = cell.value
        hyperlink = getattr(cell.hyperlink, "target", None)
        if patent_no in (None, "") and not hyperlink:
            continue
        rows.append(
            {
                "row": row_idx,
                "patent_no": patent_no,
                "hyperlink": hyperlink,
            }
        )

    print(json.dumps({"file": str(path), "rows": rows}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
