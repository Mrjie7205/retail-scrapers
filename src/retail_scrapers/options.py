"""运行参数模型。"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class CatalogOptions:
    brands: list[str] = field(default_factory=list)
    years: list[int] = field(default_factory=list)
    max_pages: int | None = None
    max_items: int | None = None
    strict: bool = True
    headless: bool = True
    postal_code: str | None = None


@dataclass(slots=True)
class PriceOptions:
    concurrency: int = 3
    min_success_rate: float = 0.8
    strict: bool = True
    headless: bool = True
    postal_code: str | None = None
