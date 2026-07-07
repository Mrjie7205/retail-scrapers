"""Amazon Germany：德国配送地会话、搜索目录和商品页价格。"""

from __future__ import annotations

import asyncio
import re
from collections.abc import Sequence
from urllib.parse import quote_plus

from ...core.browser import BrowserRuntime
from ...core.pricing import clean_price, price_from_schema
from ...errors import ExtractionError
from ...models import CatalogRecord, PriceRecord, PriceTarget
from ...options import CatalogOptions, PriceOptions
from ..base import ChannelAdapter

BASE_URL = "https://www.amazon.de"
DEFAULT_POSTAL_CODE = "10115"
SIZE_RE = re.compile(r"(\d{2,3})\s*(?:Zoll|[\"”″])", re.I)
NON_PRODUCT_RE = re.compile(
    r"projektor|beamer|monitor|signage|wandhalterung|fernbedienung|netzteil",
    re.I,
)

EXTRACT_JS = """
() => Array.from(document.querySelectorAll("div[data-component-type='s-search-result']"))
  .map(el => {
    const asin = el.getAttribute("data-asin") || "";
    const titleNode = el.querySelector("h2 span,[data-cy='title-recipe'] span,h2 a span");
    const priceNode = el.querySelector(".a-price .a-offscreen");
    const sponsored = !!el.querySelector(
      "[aria-label*='Gesponsert'],.puis-sponsored-label-text,.s-sponsored-label-text"
    );
    return {
      asin,
      title: titleNode ? (titleNode.textContent || "").trim().replace(/\\s+/g, " ") : "",
      price: priceNode ? (priceNode.textContent || "").trim() : "",
      sponsored
    };
  })
  .filter(row => row.asin && row.title);
"""

PRICE_SELECTORS = (
    "#corePriceDisplay_desktop_feature_div span.priceToPay span.a-offscreen",
    "#corePriceDisplay_desktop_feature_div .a-offscreen",
    "#corePrice_feature_div .a-offscreen",
    "#apex_offerDisplay_desktop_feature_div .a-offscreen",
    ".priceToPay .a-offscreen",
    ".a-price .a-offscreen",
)


async def _goto(page, url: str, *, timeout_ms: int, retries: int, delay_seconds: float):
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            return await page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        except Exception as exc:
            last_error = exc
            if attempt < retries:
                await asyncio.sleep(delay_seconds * (attempt + 1))
    if last_error:
        raise last_error
    return None


async def _set_location(
    page,
    postal_code: str,
    timeout_ms: int,
    retries: int,
    delay_seconds: float,
) -> bool:
    """使用Amazon自身的地址变更接口设置德国配送邮编。"""
    await page.context.add_cookies(
        [
            {"name": "i18n-prefs", "value": "EUR", "domain": ".amazon.de", "path": "/"},
            {"name": "lc-acbde", "value": "de_DE", "domain": ".amazon.de", "path": "/"},
        ]
    )
    await _goto(
        page,
        BASE_URL,
        timeout_ms=timeout_ms,
        retries=retries,
        delay_seconds=delay_seconds,
    )
    for selector in ("#sp-cc-accept", "#sp-cc-accept input"):
        try:
            await page.click(selector, timeout=1_500)
            break
        except Exception:
            pass
    html = await page.evaluate(
        """async () => {
          const url = "/portal-migration/hz/glow/get-rendered-toaster"
            + "?pageType=Gateway&aisTransitionState=null"
            + "&rancorLocationSource=IP_GEOLOCATION&isB2B=false";
          return await (await fetch(url, {credentials: "include"})).text();
        }"""
    )
    token_match = re.search(r'data-toaster-csrfToken="([^"]+)"', html)
    if not token_match:
        return False
    result = await page.evaluate(
        """async ({token, postalCode}) => {
          const response = await fetch(
            "/portal-migration/hz/glow/address-change?actionSource=glow",
            {
              method: "POST",
              headers: {
                "anti-csrftoken-a2z": token,
                "content-type": "application/json"
              },
              credentials: "include",
              body: JSON.stringify({
                locationType: "LOCATION_INPUT",
                zipCode: postalCode,
                deviceType: "web",
                storeContext: "generic",
                pageType: "Gateway",
                actionSource: "glow"
              })
            }
          );
          try {
            return (await response.json()).isAddressUpdated === 1;
          } catch {
            return false;
          }
        }""",
        {"token": token_match.group(1), "postalCode": postal_code},
    )
    return bool(result)


async def _page_price(page) -> tuple[float, str] | None:
    parsed = await price_from_schema(page)
    if parsed and parsed[1] == "EUR":
        return parsed
    text = await page.evaluate(
        """selectors => {
          for (const selector of selectors) {
            const node = document.querySelector(selector);
            if (node && node.textContent && node.textContent.trim()) {
              return node.textContent.trim();
            }
          }
          return "";
        }""",
        list(PRICE_SELECTORS),
    )
    parsed = clean_price(text)
    return parsed if parsed and parsed[1] == "EUR" else None


class AmazonDeAdapter(ChannelAdapter):
    channel_id = "amazon-de"
    display_name = "Amazon Germany"
    country = "DE"

    async def scrape_catalog(
        self,
        runtime: BrowserRuntime,
        options: CatalogOptions,
    ) -> Sequence[CatalogRecord]:
        context = await runtime.new_context(locale="de-DE", timezone_id="Europe/Berlin")
        page = await context.new_page()
        try:
            postal_code = options.postal_code or DEFAULT_POSTAL_CODE
            if not await _set_location(
                page,
                postal_code,
                options.timeout_ms,
                options.retries,
                options.delay_seconds,
            ):
                raise ExtractionError("Amazon德国配送地设置失败，拒绝输出可能属于其他市场的数据")

            queries = options.brands or [""]
            max_pages = options.max_pages or 7
            by_asin: dict[str, CatalogRecord] = {}
            for query in queries:
                for page_number in range(1, max_pages + 1):
                    search_term = f"{query} fernseher".strip()
                    url = f"{BASE_URL}/s?k={quote_plus(search_term)}&page={page_number}"
                    response = await _goto(
                        page,
                        url,
                        timeout_ms=options.timeout_ms,
                        retries=options.retries,
                        delay_seconds=options.delay_seconds,
                    )
                    if not response or response.status >= 400:
                        raise ExtractionError(
                            f"Amazon搜索页HTTP {response.status if response else 0}"
                        )
                    await page.wait_for_timeout(int(options.delay_seconds * 1000))
                    rows = await page.evaluate(EXTRACT_JS)
                    added = 0
                    for row in rows:
                        asin = str(row.get("asin") or "")
                        title = str(row.get("title") or "")
                        if (
                            not asin
                            or asin in by_asin
                            or row.get("sponsored")
                            or NON_PRODUCT_RE.search(title)
                        ):
                            continue
                        size_match = SIZE_RE.search(title)
                        if not size_match:
                            continue
                        parsed = clean_price(str(row.get("price") or ""), "EUR")
                        brand = query if query else title.split(" ", 1)[0]
                        by_asin[asin] = CatalogRecord(
                            channel=self.channel_id,
                            country=self.country,
                            sku=asin,
                            brand=brand,
                            title=title,
                            url=f"{BASE_URL}/dp/{asin}",
                            price=parsed[0] if parsed else None,
                            currency="EUR" if parsed else "",
                            size_inch=float(size_match.group(1)),
                            metadata={"postal_code": postal_code},
                        )
                        added += 1
                    if page_number > 1 and added == 0:
                        break
                    await asyncio.sleep(options.delay_seconds)
            records = list(by_asin.values())
            return records[: options.max_items] if options.max_items else records
        finally:
            await context.close()

    async def scrape_prices(
        self,
        runtime: BrowserRuntime,
        targets: Sequence[PriceTarget],
        options: PriceOptions,
    ) -> Sequence[PriceRecord]:
        context = await runtime.new_context(locale="de-DE", timezone_id="Europe/Berlin")
        page = await context.new_page()
        postal_code = options.postal_code or DEFAULT_POSTAL_CODE
        try:
            if not await _set_location(
                page,
                postal_code,
                options.timeout_ms,
                options.retries,
                options.delay_seconds,
            ):
                raise ExtractionError("Amazon德国配送地设置失败")
            records = []
            for target in targets:
                try:
                    response = await _goto(
                        page,
                        target.url,
                        timeout_ms=options.timeout_ms,
                        retries=options.retries,
                        delay_seconds=options.delay_seconds,
                    )
                    if not response or response.status >= 400:
                        raise ExtractionError(f"HTTP {response.status if response else 0}")
                    parsed = await _page_price(page)
                    if not parsed:
                        raise ExtractionError("没有找到原生EUR价格")
                    records.append(
                        PriceRecord(
                            channel=self.channel_id,
                            country=self.country,
                            id=target.id,
                            url=target.url,
                            price=parsed[0],
                            currency=parsed[1],
                            status="success",
                            title=await page.title(),
                            metadata={**target.metadata, "postal_code": postal_code},
                        )
                    )
                except Exception as exc:
                    records.append(
                        PriceRecord(
                            channel=self.channel_id,
                            country=self.country,
                            id=target.id,
                            url=target.url,
                            price=None,
                            currency="",
                            status="failed",
                            metadata={**target.metadata, "error": str(exc)[:160]},
                        )
                    )
                await asyncio.sleep(options.delay_seconds)
            return records
        finally:
            await context.close()
