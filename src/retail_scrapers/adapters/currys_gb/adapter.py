"""Currys Great Britain：隔离浏览器会话的分页目录与商品页价格。"""

from __future__ import annotations

import asyncio
import re
from collections.abc import Sequence
from urllib.parse import urljoin

from ...core.browser import BrowserRuntime
from ...core.pricing import clean_price, price_from_schema
from ...errors import CompletenessError, ExtractionError
from ...models import CatalogRecord, PriceRecord, PriceTarget
from ...options import CatalogOptions, PriceOptions
from ..base import ChannelAdapter

BASE_URL = "https://www.currys.co.uk"
CATEGORY_URL = f"{BASE_URL}/tv-and-audio/televisions/tvs"
PAGE_SIZE = 20
TOTAL_RE = re.compile(r"\bof\s+([\d,]+)\b", re.I)
SIZE_RE = re.compile(r"(\d{2,3})\s*(?:[\"”″]|-?\s*inch)", re.I)

EXTRACT_JS = """
() => {
  const rows = {};
  document.querySelectorAll("a[href*='/products/']").forEach(a => {
    const href = a.getAttribute("href") || "";
    const match = href.match(/\\/products\\/([^/?#]+)/);
    if (!match) return;
    const slug = match[1];
    const card = a.closest("article,li,[class*='product'],[data-testid*='product']");
    const title = (a.innerText || "").trim().replace(/\\s+/g, " ");
    const priceMatch = card && (card.innerText || "").match(/£[\\d,.]+/);
    if (!rows[slug]) rows[slug] = {slug, href: href.split("?")[0], title: "", price: ""};
    if (title.length > rows[slug].title.length) rows[slug].title = title;
    if (priceMatch && !rows[slug].price) rows[slug].price = priceMatch[0];
  });
  return Object.values(rows);
}
"""


def _slug_title(slug: str) -> str:
    tokens = [token for token in slug.split("-") if token]
    while tokens and tokens[-1].isdigit():
        tokens.pop()
    return " ".join(tokens)


def _brand(slug: str) -> str:
    return slug.split("-", 1)[0].replace("_", " ").title()


def _size(slug: str, title: str) -> float | None:
    for token in slug.split("-"):
        if token.isdigit() and 10 <= int(token) <= 200:
            return float(token)
    match = SIZE_RE.search(title)
    return float(match.group(1)) if match else None


class CurrysGbAdapter(ChannelAdapter):
    channel_id = "currys-gb"
    display_name = "Currys Great Britain"
    country = "GB"

    async def _page(self, runtime: BrowserRuntime, start: int) -> tuple[list[dict], int | None]:
        """Currys同一会话连续翻页容易403，因此每页使用独立context。"""
        context = await runtime.new_context(locale="en-GB", timezone_id="Europe/London")
        page = await context.new_page()
        try:
            url = f"{CATEGORY_URL}?start={start}&sz={PAGE_SIZE}"
            response = await page.goto(url, wait_until="domcontentloaded", timeout=50_000)
            if not response or response.status != 200:
                raise ExtractionError(f"Currys目录页HTTP {response.status if response else 0}")
            await page.wait_for_timeout(2_000)
            rows = await page.evaluate(EXTRACT_JS)
            body = await page.locator("body").inner_text()
            match = TOTAL_RE.search(body)
            expected = int(match.group(1).replace(",", "")) if match else None
            return rows or [], expected
        finally:
            await context.close()

    async def scrape_catalog(
        self,
        runtime: BrowserRuntime,
        options: CatalogOptions,
    ) -> Sequence[CatalogRecord]:
        by_slug: dict[str, dict] = {}
        expected: int | None = None
        max_pages = options.max_pages or 30

        for page_index in range(max_pages):
            rows: list[dict] = []
            page_expected = None
            last_error = None
            for attempt in range(2):
                try:
                    rows, page_expected = await self._page(runtime, page_index * PAGE_SIZE)
                    last_error = None
                    break
                except Exception as exc:
                    last_error = exc
                    await asyncio.sleep(attempt + 1)
            if last_error:
                raise ExtractionError(f"Currys分页失败: {last_error}")
            if page_expected is not None:
                if expected is not None and expected != page_expected:
                    raise CompletenessError("Currys分页过程中商品总量发生变化")
                expected = page_expected

            added = 0
            for row in rows:
                slug = str(row.get("slug") or "").removesuffix(".html")
                if not slug or slug in by_slug:
                    continue
                brand = _brand(slug)
                if options.brands and brand.lower() not in {
                    value.lower() for value in options.brands
                }:
                    continue
                by_slug[slug] = row
                added += 1

            if not options.brands and expected is not None and len(by_slug) >= expected:
                break
            if page_index > 0 and not rows:
                break
            if page_index > 0 and added == 0 and not options.brands:
                break
            await asyncio.sleep(1)

        records = []
        for slug, row in by_slug.items():
            # 可见标题常被促销浮层污染；slug包含品牌、型号和尺寸，稳定性更高。
            title = _slug_title(slug)
            parsed = clean_price(str(row.get("price") or ""), "GBP")
            records.append(
                CatalogRecord(
                    channel=self.channel_id,
                    country=self.country,
                    sku=slug,
                    brand=_brand(slug),
                    title=title,
                    url=urljoin(BASE_URL, str(row.get("href") or "")),
                    price=parsed[0] if parsed else None,
                    currency="GBP" if parsed else "",
                    size_inch=_size(slug, title),
                )
            )

        full_unfiltered = not options.brands and options.max_pages is None
        if options.strict and full_unfiltered and expected is not None and len(records) != expected:
            raise CompletenessError(f"Currys目录不完整: {len(records)} != {expected}")
        return records[: options.max_items] if options.max_items else records

    async def scrape_prices(
        self,
        runtime: BrowserRuntime,
        targets: Sequence[PriceTarget],
        options: PriceOptions,
    ) -> Sequence[PriceRecord]:
        semaphore = asyncio.Semaphore(max(1, options.concurrency))

        async def one(target: PriceTarget) -> PriceRecord:
            async with semaphore:
                context = await runtime.new_context(locale="en-GB", timezone_id="Europe/London")
                page = await context.new_page()
                try:
                    response = await page.goto(
                        target.url,
                        wait_until="domcontentloaded",
                        timeout=60_000,
                    )
                    if not response or response.status >= 400:
                        raise ExtractionError(f"HTTP {response.status if response else 0}")
                    parsed = await price_from_schema(page)
                    if not parsed:
                        for selector in (
                            "[data-testid*='price']",
                            "[class*='current-price']",
                            "[class*='price']",
                        ):
                            try:
                                text = await page.locator(selector).first.text_content(
                                    timeout=1_000
                                )
                            except Exception:
                                continue
                            parsed = clean_price(text or "", "GBP")
                            if parsed:
                                break
                    if not parsed or parsed[1] != "GBP":
                        raise ExtractionError("没有找到GBP价格")
                    return PriceRecord(
                        channel=self.channel_id,
                        country=self.country,
                        id=target.id,
                        url=target.url,
                        price=parsed[0],
                        currency=parsed[1],
                        status="success",
                        title=await page.title(),
                        metadata=target.metadata,
                    )
                except Exception as exc:
                    return PriceRecord(
                        channel=self.channel_id,
                        country=self.country,
                        id=target.id,
                        url=target.url,
                        price=None,
                        currency="",
                        status="failed",
                        metadata={**target.metadata, "error": str(exc)[:160]},
                    )
                finally:
                    await context.close()

        return await asyncio.gather(*(one(target) for target in targets))
