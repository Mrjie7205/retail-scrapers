"""通用价格文本与Schema.org解析。"""

from __future__ import annotations

import json
import re
from decimal import Decimal
from typing import Any


def clean_price(text: str, currency_hint: str = "") -> tuple[float, str] | None:
    raw = (text or "").replace("\xa0", " ").strip()
    if not raw:
        return None

    currency = currency_hint.upper().strip()
    if not currency:
        if "£" in raw or re.search(r"\bGBP\b", raw, re.I):
            currency = "GBP"
        elif re.search(r"\bNOK\b|\bkr\b", raw, re.I):
            currency = "NOK"
        elif "$" in raw or re.search(r"\bUSD\b", raw, re.I):
            currency = "USD"
        elif "€" in raw or re.search(r"\bEUR\b", raw, re.I):
            currency = "EUR"

    match = re.search(r"\d[\d\s.,]*", raw)
    if not match:
        return None
    value = match.group(0).replace(" ", "")

    if "," in value and "." in value:
        if value.rfind(",") > value.rfind("."):
            value = value.replace(".", "").replace(",", ".")
        else:
            value = value.replace(",", "")
    elif "," in value:
        tail = value.rsplit(",", 1)[-1]
        value = value.replace(",", ".") if len(tail) in {1, 2} else value.replace(",", "")
    elif value.count(".") > 1:
        value = value.replace(".", "")
    elif "." in value:
        tail = value.rsplit(".", 1)[-1]
        if len(tail) == 3:
            value = value.replace(".", "")

    try:
        price = float(Decimal(value))
    except Exception:
        return None
    if price <= 0:
        return None
    return price, currency


def _schema_objects(value: Any):
    if isinstance(value, dict):
        yield value
        for nested in value.values():
            yield from _schema_objects(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _schema_objects(nested)


async def price_from_schema(page) -> tuple[float, str] | None:
    """依次读取机器可读meta和JSON-LD，避免误取划线价或分期价。"""
    amount = await page.get_attribute(
        "meta[property='product:price:amount']", "content"
    ) or await page.get_attribute("meta[itemprop='price']", "content")
    if amount:
        currency = (
            await page.get_attribute("meta[property='product:price:currency']", "content")
            or await page.get_attribute("meta[itemprop='priceCurrency']", "content")
            or ""
        )
        parsed = clean_price(amount, currency)
        if parsed:
            return parsed

    for node in await page.locator("script[type='application/ld+json']").all():
        try:
            payload = json.loads(await node.text_content() or "")
        except (json.JSONDecodeError, TypeError):
            continue
        for obj in _schema_objects(payload):
            offers = obj.get("offers")
            if isinstance(offers, list):
                offers = offers[0] if offers else None
            if not isinstance(offers, dict):
                continue
            parsed = clean_price(
                str(offers.get("price") or offers.get("lowPrice") or ""),
                str(offers.get("priceCurrency") or ""),
            )
            if parsed:
                return parsed
    return None
