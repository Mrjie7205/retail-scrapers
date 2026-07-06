"""Boulanger France：品牌facet目录 + Schema.org价格。"""

from __future__ import annotations

import asyncio
import json
import re
from collections.abc import Sequence
from typing import Any, cast
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup

from ...core.browser import BrowserRuntime
from ...core.pricing import clean_price, price_from_schema
from ...errors import ExtractionError
from ...models import CatalogRecord, PriceRecord, PriceTarget
from ...options import CatalogOptions, PriceOptions
from ..base import ChannelAdapter

BASE_URL = "https://www.boulanger.com"
CATEGORY_URL = f"{BASE_URL}/c/televiseur"
PRODUCT_SELECTOR = "a[href*='/ref/']"
COOKIE_SELECTOR = "#onetrust-accept-btn-handler"
MODEL_LIKE = re.compile(r"[A-Z]\d|\d[A-Z]", re.I)
SIZE_RE = re.compile(r"(\d{2,3})\s*(?:pouces?|[\"”″])", re.I)

PRICE_TEXT_RE = re.compile(r"\d[\d\s]*(?:[,.]\d{2})?\s*€")


def _catalog_url(brand: str | None, page: int) -> str:
    base = CATEGORY_URL if not brand else f"{CATEGORY_URL}/brand~{brand.lower()}"
    return base if page == 1 else f"{base}?numPage={page}"


def _sku_from_url(url: str) -> str:
    parts = urlsplit(url).path.rstrip("/").split("/")
    try:
        return parts[parts.index("ref") + 1]
    except (ValueError, IndexError):
        return url


def _size(text: str) -> float | None:
    match = SIZE_RE.search(text)
    if not match:
        return None
    value = float(match.group(1))
    return value if 10 <= value <= 200 else None


def _brand(text: str, selected_brand: str | None) -> str:
    if selected_brand:
        return selected_brand
    words = cast(list[str], re.findall(r"[A-Za-zÀ-ÿ]+", text))
    if words and words[0].lower() == "tv" and len(words) > 1:
        return words[1]
    return words[0] if words else ""


def _best_title(values: list[str]) -> str:
    candidates = [value for value in values if 8 <= len(value) <= 220 and MODEL_LIKE.search(value)]
    if not candidates:
        return ""
    return max(candidates, key=lambda value: (value.lower().startswith("tv "), -len(value)))


class BoulangerFrAdapter(ChannelAdapter):
    channel_id = "boulanger-fr"
    display_name = "Boulanger France"
    country = "FR"

    @staticmethod
    def _rows_from_html(html: str) -> list[dict[str, str]]:
        """Boulanger当前目录HTML已包含商品卡，优先直接解析以减少浏览器拦截。"""
        soup = BeautifulSoup(html, "html.parser")
        rows = []
        for anchor in soup.select('a[href*="/ref/"]'):
            href = str(anchor.get("href") or "")
            if "/ref/" not in href:
                continue
            texts = [
                anchor.get_text(" ", strip=True),
                str(anchor.get("title") or ""),
                str(anchor.get("aria-label") or ""),
            ]
            card: Any = anchor.find_parent("li", class_=re.compile(r"\bproduct-list__item\b"))
            price_node = card.select_one(".price__amount") if card else None
            price_text = price_node.get_text(" ", strip=True) if price_node else ""
            price_match = PRICE_TEXT_RE.search(price_text)
            for text in texts:
                if text:
                    rows.append(
                        {
                            "href": href,
                            "text": re.sub(r"\s+", " ", text).strip(),
                            "price": price_match.group(0) if price_match else "",
                        }
                    )
        return rows

    @staticmethod
    def _price_from_html(html: str) -> tuple[float, str] | None:
        soup = BeautifulSoup(html, "html.parser")
        for node in soup.select('script[type="application/ld+json"]'):
            try:
                payload = json.loads(node.get_text())
            except (json.JSONDecodeError, TypeError):
                continue
            objects = payload if isinstance(payload, list) else [payload]
            for obj in objects:
                if not isinstance(obj, dict):
                    continue
                offers = obj.get("offers")
                if isinstance(offers, list):
                    offers = offers[0] if offers else None
                if not isinstance(offers, dict):
                    continue
                parsed = clean_price(
                    str(offers.get("price") or offers.get("lowPrice") or ""),
                    str(offers.get("priceCurrency") or "EUR"),
                )
                if parsed:
                    return parsed
        return None

    async def scrape_catalog(
        self,
        runtime: BrowserRuntime,
        options: CatalogOptions,
    ) -> Sequence[CatalogRecord]:
        request = await runtime.new_request_context(locale="fr-FR", referer=BASE_URL)
        by_url: dict[str, dict[str, Any]] = {}
        try:
            brand_filters: list[str | None] = list(options.brands) if options.brands else [None]
            max_pages = options.max_pages or 8
            for selected_brand in brand_filters:
                for page_number in range(1, max_pages + 1):
                    url = _catalog_url(selected_brand, page_number)
                    response = await request.get(
                        url,
                        headers={"accept": "text/html"},
                        timeout=30_000,
                    )
                    if not response.ok:
                        raise ExtractionError(f"Boulanger目录页HTTP {response.status}: {url}")
                    extracted = self._rows_from_html(await response.text())
                    added = 0
                    for row in extracted:
                        canonical = urljoin(BASE_URL, row.get("href") or "").split("#", 1)[0]
                        if "/ref/" not in canonical:
                            continue
                        if canonical not in by_url:
                            by_url[canonical] = {
                                "texts": [],
                                "prices": [],
                                "brand": selected_brand or "",
                            }
                            added += 1
                        if row.get("text"):
                            by_url[canonical]["texts"].append(row["text"])
                        if row.get("price"):
                            by_url[canonical]["prices"].append(row["price"])
                    if page_number > 1 and added == 0:
                        break

            records = []
            for url, row in by_url.items():
                title = _best_title(list(row["texts"]))
                if not title:
                    continue
                prices = [
                    parsed[0] for text in row["prices"] if (parsed := clean_price(text, "EUR"))
                ]
                records.append(
                    CatalogRecord(
                        channel=self.channel_id,
                        country=self.country,
                        sku=_sku_from_url(url),
                        brand=_brand(title, str(row["brand"]) or None),
                        title=title,
                        url=url,
                        price=min(prices) if prices else None,
                        currency="EUR" if prices else "",
                        size_inch=_size(title),
                    )
                )
            return records[: options.max_items] if options.max_items else records
        finally:
            await request.dispose()

    async def scrape_prices(
        self,
        runtime: BrowserRuntime,
        targets: Sequence[PriceTarget],
        options: PriceOptions,
    ) -> Sequence[PriceRecord]:
        semaphore = asyncio.Semaphore(max(1, options.concurrency))
        request = await runtime.new_request_context(locale="fr-FR", referer=BASE_URL)

        async def one(target: PriceTarget) -> PriceRecord:
            async with semaphore:
                try:
                    response = await request.get(
                        target.url,
                        headers={"accept": "text/html"},
                        timeout=30_000,
                    )
                    if response.ok:
                        parsed = self._price_from_html(await response.text())
                        if parsed and parsed[1] == "EUR":
                            return PriceRecord(
                                channel=self.channel_id,
                                country=self.country,
                                id=target.id,
                                url=target.url,
                                price=parsed[0],
                                currency=parsed[1],
                                status="success",
                                metadata={**target.metadata, "source": "html-schema"},
                            )
                except Exception:
                    pass

                context = await runtime.new_context(locale="fr-FR", timezone_id="Europe/Paris")
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
                            ".price__amount",
                            "[data-test*='price']",
                            "[class*='price-amount']",
                        ):
                            try:
                                text = await page.locator(selector).first.text_content(
                                    timeout=1_000
                                )
                            except Exception:
                                continue
                            parsed = clean_price(text or "", "EUR")
                            if parsed:
                                break
                    if not parsed or parsed[1] != "EUR":
                        raise ExtractionError("没有找到EUR价格")
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

        try:
            return await asyncio.gather(*(one(target) for target in targets))
        finally:
            await request.dispose()
