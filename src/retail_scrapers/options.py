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
    timeout_ms: int = 60_000
    retries: int = 2
    delay_seconds: float = 1.0

    def __post_init__(self) -> None:
        _validate_runtime_options(self.timeout_ms, self.retries, self.delay_seconds)


@dataclass(slots=True)
class PriceOptions:
    concurrency: int = 3
    min_success_rate: float = 0.8
    strict: bool = True
    headless: bool = True
    postal_code: str | None = None
    timeout_ms: int = 60_000
    retries: int = 2
    delay_seconds: float = 1.0

    def __post_init__(self) -> None:
        _validate_runtime_options(self.timeout_ms, self.retries, self.delay_seconds)


def _validate_runtime_options(timeout_ms: int, retries: int, delay_seconds: float) -> None:
    if timeout_ms <= 0:
        raise ValueError("timeout_ms must be greater than 0")
    if retries < 0:
        raise ValueError("retries must be greater than or equal to 0")
    if delay_seconds < 0:
        raise ValueError("delay_seconds must be greater than or equal to 0")
