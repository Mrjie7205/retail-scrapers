"""Python API：负责创建运行时并调用渠道adapter。"""

from __future__ import annotations

import asyncio
from collections.abc import Sequence

from .core.browser import BrowserRuntime
from .models import CatalogRecord, PriceRecord, PriceTarget
from .options import CatalogOptions, PriceOptions
from .registry import get_adapter
from .validation import validate_catalog, validate_price_run


async def scrape_catalog_async(
    channel: str,
    *,
    brands: Sequence[str] = (),
    years: Sequence[int] = (),
    max_pages: int | None = None,
    max_items: int | None = None,
    strict: bool = True,
    headless: bool = True,
    postal_code: str | None = None,
    timeout_ms: int = 60_000,
    retries: int = 2,
    delay_seconds: float = 1.0,
) -> list[CatalogRecord]:
    adapter = get_adapter(channel)
    options = CatalogOptions(
        brands=list(brands),
        years=list(years),
        max_pages=max_pages,
        max_items=max_items,
        strict=strict,
        headless=headless,
        postal_code=postal_code,
        timeout_ms=timeout_ms,
        retries=retries,
        delay_seconds=delay_seconds,
    )
    async with BrowserRuntime(headless=headless) as runtime:
        records = list(await adapter.scrape_catalog(runtime, options))
    return validate_catalog(records) if strict else records


def scrape_catalog(channel: str, **kwargs) -> list[CatalogRecord]:
    return asyncio.run(scrape_catalog_async(channel, **kwargs))


async def scrape_prices_async(
    channel: str,
    targets: Sequence[PriceTarget],
    *,
    concurrency: int = 3,
    min_success_rate: float = 0.8,
    strict: bool = True,
    headless: bool = True,
    postal_code: str | None = None,
    timeout_ms: int = 60_000,
    retries: int = 2,
    delay_seconds: float = 1.0,
) -> list[PriceRecord]:
    adapter = get_adapter(channel)
    options = PriceOptions(
        concurrency=concurrency,
        min_success_rate=min_success_rate,
        strict=strict,
        headless=headless,
        postal_code=postal_code,
        timeout_ms=timeout_ms,
        retries=retries,
        delay_seconds=delay_seconds,
    )
    async with BrowserRuntime(headless=headless) as runtime:
        records = list(await adapter.scrape_prices(runtime, targets, options))
    if strict:
        return validate_price_run(records, minimum_success_rate=min_success_rate)
    return records


def scrape_prices(
    channel: str,
    targets: Sequence[PriceTarget],
    **kwargs,
) -> list[PriceRecord]:
    return asyncio.run(scrape_prices_async(channel, targets, **kwargs))
