"""Elkjøp Norway：Algolia目录 + tRPC价格。"""

from __future__ import annotations

import asyncio
import json
import re
from collections.abc import Sequence
from typing import Any, cast
from urllib.parse import quote

from ...core.browser import BrowserRuntime
from ...core.pricing import price_from_schema
from ...errors import CompletenessError, ExtractionError
from ...models import CatalogRecord, PriceRecord, PriceTarget
from ...options import CatalogOptions, PriceOptions
from ...validation import validate_catalog
from ..base import ChannelAdapter

HOME_URL = "https://www.elkjop.no/"
SIGNED_KEY_URL = f"{HOME_URL}api/algolia/signed-api-key"
ALGOLIA_URL = "https://z0fl7r8ubh-dsn.algolia.net/1/indexes/*/queries"
ALGOLIA_APP_ID = "Z0FL7R8UBH"
ALGOLIA_INDEX = "commerce_b2c_OCNOELK"
TV_TAXONOMY = "productTaxonomy.id:PT351"
PRICE_API = f"{HOME_URL}api/trpc/product.getDynamicProductData"
PAGE_SIZE = 48
SKU_RE = re.compile(r"/(\d{5,9})(?:[/?#]|$)")


def _first(value):
    return value[0] if isinstance(value, list) and value else value


def _year(hit: dict) -> int | None:
    value = _first((hit.get("attributes") or {}).get("33627"))
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _size(hit: dict) -> float | None:
    value = _first((hit.get("attributes") or {}).get("31323"))
    try:
        size = float(value)
    except (TypeError, ValueError):
        return None
    return size if 10 <= size <= 200 else None


def _availability(hit: dict) -> str:
    if hit.get("isBuyableOnline") or hit.get("isOnline"):
        return "in_stock"
    status = str(hit.get("onlineSalesStatus") or "").upper()
    return "unavailable" if status else "unknown"


class ElkjopNoAdapter(ChannelAdapter):
    channel_id = "elkjop-no"
    display_name = "Elkjøp Norway"
    country = "NO"

    async def _signed_key(self, request) -> str:
        last_error = ""
        for attempt in range(3):
            try:
                response = await request.get(
                    SIGNED_KEY_URL,
                    headers={"accept": "application/json", "referer": HOME_URL},
                    timeout=30_000,
                )
                if response.ok:
                    key = str((await response.json()).get("apiKey") or "")
                    if key:
                        return key
                last_error = f"HTTP {response.status}"
            except Exception as exc:
                last_error = str(exc)
            await asyncio.sleep(attempt + 1)
        raise ExtractionError(f"无法获取Elkjøp搜索凭据: {last_error[:120]}")

    @staticmethod
    def _payload(options: CatalogOptions, year: int | None, page: int) -> dict:
        facets = []
        if year is not None:
            facets.append([f"attributes.33627:{year}"])
        if options.brands:
            facets.append([f"brand:{brand}" for brand in options.brands])
        return {
            "requests": [
                {
                    "indexName": ALGOLIA_INDEX,
                    "query": "",
                    "facetFilters": facets,
                    "filters": TV_TAXONOMY,
                    "attributesToRetrieve": [
                        "articleNumber",
                        "objectID",
                        "brand",
                        "title",
                        "name",
                        "manufacturerArticleNumber",
                        "productUrl",
                        "urlB2C",
                        "price",
                        "attributes",
                        "isOnline",
                        "isBuyableOnline",
                        "onlineSalesStatus",
                    ],
                    "hitsPerPage": PAGE_SIZE,
                    "page": page,
                    "analytics": False,
                    "clickAnalytics": False,
                }
            ]
        }

    async def _query(self, request, key: str, options: CatalogOptions, year, page) -> dict:
        last_error = ""
        for attempt in range(3):
            try:
                response = await request.post(
                    ALGOLIA_URL,
                    headers={
                        "content-type": "application/json",
                        "x-algolia-application-id": ALGOLIA_APP_ID,
                        "x-algolia-api-key": key,
                    },
                    data=json.dumps(self._payload(options, year, page)),
                    timeout=30_000,
                )
                if response.ok:
                    results = (await response.json()).get("results") or []
                    if results:
                        return cast(dict[str, Any], results[0])
                last_error = f"HTTP {response.status}"
            except Exception as exc:
                last_error = str(exc)
            await asyncio.sleep(attempt + 1)
        raise ExtractionError(f"Elkjøp目录API失败: {last_error[:120]}")

    async def scrape_catalog(
        self,
        runtime: BrowserRuntime,
        options: CatalogOptions,
    ) -> Sequence[CatalogRecord]:
        request = await runtime.new_request_context(locale="nb-NO", referer=HOME_URL)
        try:
            key = await self._signed_key(request)
            groups: list[int | None] = list(options.years) if options.years else [None]
            by_sku: dict[str, CatalogRecord] = {}

            for selected_year in groups:
                first = await self._query(request, key, options, selected_year, 0)
                expected = int(first.get("nbHits") or 0)
                pages = int(first.get("nbPages") or 0)
                if expected <= 0 or pages <= 0:
                    raise CompletenessError(
                        f"筛选条件没有返回商品: year={selected_year}, brands={options.brands}"
                    )
                if options.max_pages:
                    pages = min(pages, options.max_pages)

                group_skus: set[str] = set()
                for page_index in range(pages):
                    result = (
                        first
                        if page_index == 0
                        else await self._query(request, key, options, selected_year, page_index)
                    )
                    if int(result.get("nbHits") or 0) != expected:
                        raise CompletenessError("Elkjøp分页过程中总量发生变化")
                    for hit in result.get("hits") or []:
                        sku = str(hit.get("articleNumber") or hit.get("objectID") or "")
                        url = str(hit.get("productUrl") or hit.get("urlB2C") or "")
                        if not sku or not url or sku in group_skus:
                            raise CompletenessError(f"Elkjøp返回无效或重复SKU: {sku!r}")
                        group_skus.add(sku)

                        price_data = hit.get("price") or {}
                        currency = str(price_data.get("currency") or "")
                        amount = price_data.get("amount")
                        price = (
                            float(amount)
                            if isinstance(amount, (int, float, str)) and amount != ""
                            else None
                        )
                        brand = str(hit.get("brand") or "")
                        title = str(hit.get("title") or hit.get("name") or "")
                        model = str(hit.get("manufacturerArticleNumber") or "")
                        record_year = _year(hit)
                        if selected_year is not None and record_year != selected_year:
                            raise CompletenessError(
                                f"Elkjøp SKU {sku} 年份 {record_year} 与筛选值不一致"
                            )
                        if sku in by_sku:
                            raise CompletenessError(f"Elkjøp SKU {sku} 跨筛选组重复")
                        by_sku[sku] = CatalogRecord(
                            channel=self.channel_id,
                            country=self.country,
                            sku=sku,
                            brand=brand,
                            title=title,
                            url=url.rstrip("/"),
                            price=price,
                            currency=currency,
                            availability=_availability(hit),
                            model=model,
                            model_year=record_year,
                            size_inch=_size(hit),
                        )

                full_group = options.max_pages is None or pages == int(first.get("nbPages") or 0)
                if options.strict and full_group and len(group_skus) != expected:
                    raise CompletenessError(f"Elkjøp目录不完整: {len(group_skus)} != {expected}")

            records = list(by_sku.values())
            if options.max_items:
                records = records[: options.max_items]
            if options.strict and not options.max_items:
                validate_catalog(records)
            return records
        finally:
            await request.dispose()

    @staticmethod
    async def _direct_price(request, target: PriceTarget) -> PriceRecord:
        match = SKU_RE.search(target.url)
        if not match:
            return PriceRecord(
                channel="elkjop-no",
                country="NO",
                id=target.id,
                url=target.url,
                price=None,
                currency="",
                status="failed",
                metadata={"error": "URL中没有Elkjøp SKU"},
            )
        sku = match.group(1)
        payload = json.dumps({"0": {"sku": sku}}, separators=(",", ":"))
        response = await request.get(
            f"{PRICE_API}?batch=1&input={quote(payload, safe='')}",
            headers={"accept": "application/json", "referer": target.url},
            timeout=30_000,
        )
        if not response.ok:
            raise ExtractionError(f"Elkjøp价格API HTTP {response.status}")
        data = (await response.json())[0]["result"]["data"]
        price = data.get("price") or {}
        values = price.get("current") or []
        amount = float(values[0]) if values else None
        currency = str(price.get("currency") or "")
        sellability = data.get("sellability") or {}
        available = not (sellability.get("isDisabled") or sellability.get("isDiscontinued"))
        if amount is None or currency != "NOK":
            raise ExtractionError("Elkjøp价格响应缺少NOK含税价")
        return PriceRecord(
            channel="elkjop-no",
            country="NO",
            id=target.id,
            url=target.url,
            price=amount,
            currency=currency,
            status="success",
            availability="in_stock" if available else "unavailable",
            metadata={**target.metadata, "sku": sku, "source": "trpc"},
        )

    async def _page_fallback(
        self,
        runtime: BrowserRuntime,
        target: PriceTarget,
    ) -> PriceRecord:
        context = await runtime.new_context(locale="nb-NO", timezone_id="Europe/Oslo")
        page = await context.new_page()
        try:
            await page.goto(target.url, wait_until="domcontentloaded", timeout=60_000)
            parsed = await price_from_schema(page)
            if not parsed or parsed[1] != "NOK":
                raise ExtractionError("商品页没有找到NOK价格")
            return PriceRecord(
                channel=self.channel_id,
                country=self.country,
                id=target.id,
                url=target.url,
                price=parsed[0],
                currency=parsed[1],
                status="success",
                title=await page.title(),
                metadata={**target.metadata, "source": "page"},
            )
        finally:
            await context.close()

    async def scrape_prices(
        self,
        runtime: BrowserRuntime,
        targets: Sequence[PriceTarget],
        options: PriceOptions,
    ) -> Sequence[PriceRecord]:
        request = await runtime.new_request_context(locale="nb-NO", referer=HOME_URL)
        semaphore = asyncio.Semaphore(max(1, options.concurrency))

        async def one(target: PriceTarget) -> PriceRecord:
            async with semaphore:
                try:
                    return await self._direct_price(request, target)
                except Exception as api_error:
                    try:
                        return await self._page_fallback(runtime, target)
                    except Exception as page_error:
                        return PriceRecord(
                            channel=self.channel_id,
                            country=self.country,
                            id=target.id,
                            url=target.url,
                            price=None,
                            currency="",
                            status="failed",
                            metadata={
                                **target.metadata,
                                "api_error": str(api_error)[:160],
                                "page_error": str(page_error)[:160],
                            },
                        )

        try:
            return await asyncio.gather(*(one(target) for target in targets))
        finally:
            await request.dispose()
