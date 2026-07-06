"""把记录写到标准输出、CSV或JSONL。"""

from __future__ import annotations

import csv
import json
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any, TextIO


def _flatten(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return value


def write_records(
    records: Iterable[Any],
    *,
    output: str | Path | None,
    output_format: str,
) -> None:
    rows = [r.to_dict() if hasattr(r, "to_dict") else dict(r) for r in records]
    if output_format not in {"jsonl", "csv"}:
        raise ValueError(f"不支持的输出格式: {output_format}")

    stream: TextIO
    close_stream = False
    if output:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        stream = path.open("w", encoding="utf-8", newline="")
        close_stream = True
    else:
        stream = sys.stdout

    try:
        if output_format == "jsonl":
            for row in rows:
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        elif rows:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            for row in rows:
                writer.writerow({key: _flatten(value) for key, value in row.items()})
    finally:
        if close_stream:
            stream.close()
