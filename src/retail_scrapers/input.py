"""读取用户提供的价格目标清单。"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from .errors import ConfigurationError
from .models import PriceTarget


def read_targets(path: str | Path) -> list[PriceTarget]:
    source = Path(path)
    if not source.exists():
        raise ConfigurationError(f"输入文件不存在: {source}")

    rows: list[dict]
    if source.suffix.lower() == ".jsonl":
        rows = [
            json.loads(line)
            for line in source.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    else:
        with source.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))

    targets = []
    for index, row in enumerate(rows, start=1):
        url = str(row.get("url") or "").strip()
        if not url:
            raise ConfigurationError(f"输入第 {index} 行缺少 url")
        target_id = str(row.get("id") or row.get("sku") or index).strip()
        metadata = {k: v for k, v in row.items() if k not in {"id", "sku", "url"}}
        targets.append(PriceTarget(id=target_id, url=url, metadata=metadata))
    return targets
