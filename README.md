# Retail Scrapers

[中文文档](README.zh-CN.md)

A lightweight Python toolkit for extracting product catalogs and current prices from real retail websites.

Retail Scrapers focuses on one job: turning public retail pages and frontend APIs into structured records. It does not include a database, price-history system, currency conversion layer, product matching logic, alerting, or dashboards. Those downstream choices are intentionally left to the user.

## What it does

- API-first extraction: reuse public frontend data calls when a retailer exposes them.
- Browser fallback: use Playwright when a page needs rendering or session setup.
- Channel isolation: each retailer lives in its own adapter.
- Shared output format: catalog and price records can be written as JSONL or CSV.
- Validation built in: check catalog completeness, duplicated SKUs, and price-run success rate.
- No bundled scraped data: the repository does not store user results, accounts, cookies, sessions, or private business mapping tables.

## Supported channels

| Channel ID | Market | Catalog | Price | Main strategy |
|---|---|---:|---:|---|
| `amazon-de` | Germany | Yes | Yes | Playwright, delivery-location session, EUR validation |
| `boulanger-fr` | France | Yes | Yes | Brand facets, HTML parsing, Schema.org fallback |
| `currys-gb` | United Kingdom | Yes | Yes | Isolated page sessions, Schema.org fallback |
| `elkjop-no` | Norway | Yes | Yes | Algolia catalog API, tRPC price API, page fallback |

Retail websites change frequently. Treat the latest run log or live smoke test as the source of truth for whether an adapter is currently healthy.

## Installation

```bash
python -m pip install -e .
python -m playwright install chromium
```

For development:

```bash
python -m pip install -e ".[dev]"
```

## CLI usage

List available channels:

```bash
retail-scrape channels
```

Scrape an Elkjøp TV catalog for selected years:

```bash
retail-scrape catalog \
  --channel elkjop-no \
  --year 2025 \
  --year 2026 \
  --output output/elkjop.jsonl
```

Scrape an Amazon Germany search catalog by brand:

```bash
retail-scrape catalog \
  --channel amazon-de \
  --brand Samsung \
  --brand Sony \
  --postal-code 10115 \
  --output output/amazon.csv \
  --format csv
```

Scrape prices from a URL list:

```bash
retail-scrape prices \
  --channel currys-gb \
  --input examples/products.example.csv \
  --output output/prices.jsonl
```

The input file must contain at least `id` and `url`:

```csv
id,url
product-1,https://www.example.com/product/1
product-2,https://www.example.com/product/2
```

Strict mode is enabled by default. The command exits with a non-zero status if the price success rate is below 80%, or if a catalog adapter that supports total-count validation detects missing pages. Use `--no-strict` for exploration and debugging.

Common runtime controls:

- `--timeout-ms`: request or page-navigation timeout in milliseconds.
- `--retries`: retry attempts after the first request.
- `--delay-seconds`: delay between retries, pages, or sequential product visits.

## Python API

```python
from retail_scrapers import scrape_catalog

records = scrape_catalog(
    "elkjop-no",
    years=[2025, 2026],
)

for record in records:
    print(record.sku, record.price, record.currency)
```

Async applications can use `scrape_catalog_async` and `scrape_prices_async` from `retail_scrapers.runner`.

## Output principles

- Preserve the retailer's native currency; no default currency conversion.
- Do not match products to a user's internal master-data model.
- Do not persist cookies, sessions, or scrape results inside the package.
- Keep `metadata` limited to helpful public fields returned by the retailer.

## Responsible use

Users are responsible for checking each target website's terms of service, robots rules, and applicable laws. Keep request rates reasonable, do not access data that requires login or authorization, do not collect personal information, and do not use this project to disrupt website services.

## Development

```bash
ruff check .
pytest
mypy src/retail_scrapers
```

For adapter design, see [docs/architecture.md](docs/architecture.md). For adding a new channel, see [docs/add-channel.md](docs/add-channel.md).

## License

MIT
