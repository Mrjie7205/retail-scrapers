"""跨渠道统一的数据模型。"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(slots=True)
class CatalogRecord:
    channel: str
    country: str
    sku: str
    brand: str
    title: str
    url: str
    price: float | None = None
    currency: str = ""
    availability: str = ""
    model: str = ""
    model_year: int | None = None
    size_inch: float | None = None
    scraped_at: str = field(default_factory=utc_now_iso)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class PriceTarget:
    id: str
    url: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PriceRecord:
    channel: str
    country: str
    id: str
    url: str
    price: float | None
    currency: str
    status: str
    title: str = ""
    availability: str = ""
    scraped_at: str = field(default_factory=utc_now_iso)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
