"""Retail Scrapers：真实零售网站的结构化目录与价格提取工具。"""

from .models import CatalogRecord, PriceRecord, PriceTarget
from .runner import scrape_catalog, scrape_prices

__all__ = [
    "CatalogRecord",
    "PriceRecord",
    "PriceTarget",
    "scrape_catalog",
    "scrape_prices",
]

__version__ = "0.1.0"
