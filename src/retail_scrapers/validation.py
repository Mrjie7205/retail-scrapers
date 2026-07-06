"""跨渠道通用的质量与完整性检查。"""

from __future__ import annotations

from collections.abc import Iterable

from .errors import CompletenessError
from .models import CatalogRecord, PriceRecord


def validate_catalog(
    records: Iterable[CatalogRecord],
    *,
    expected_count: int | None = None,
    minimum_count: int = 1,
) -> list[CatalogRecord]:
    rows = list(records)
    if len(rows) < minimum_count:
        raise CompletenessError(f"目录只有 {len(rows)} 条，低于最低要求 {minimum_count}")

    keys = [(r.channel, r.sku or r.url) for r in rows]
    if len(set(keys)) != len(keys):
        raise CompletenessError("目录存在重复 SKU/URL")

    for row in rows:
        if not row.channel or not row.country or not row.url or not row.title:
            raise CompletenessError(f"目录记录缺少必填字段: {row}")
        if row.price is not None and (row.price <= 0 or not row.currency):
            raise CompletenessError(f"目录价格或币种异常: {row.sku}")

    if expected_count is not None and len(rows) != expected_count:
        raise CompletenessError(
            f"目录唯一记录 {len(rows)} 条，与来源声明的 {expected_count} 条不一致"
        )
    return rows


def validate_price_run(
    records: Iterable[PriceRecord],
    *,
    minimum_success_rate: float,
) -> list[PriceRecord]:
    rows = list(records)
    if not rows:
        raise CompletenessError("价格任务没有产生任何结果")
    success = [r for r in rows if r.status == "success" and r.price is not None]
    rate = len(success) / len(rows)
    if rate < minimum_success_rate:
        raise CompletenessError(
            f"价格抓取成功率 {rate:.1%}，低于最低要求 {minimum_success_rate:.1%}"
        )
    return rows
