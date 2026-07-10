# Retail Scrapers

[中文文档](README.zh-CN.md)

![Retail Scrapers social preview](assets/social-preview.png)

![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-alpha-orange)
![Output](https://img.shields.io/badge/output-JSONL%20%7C%20CSV-0f766e)

API-first product catalog and price extraction for real retail websites.

Retail Scrapers focuses on one job: turning public retail pages and frontend APIs into structured records. It does not include a database, price-history system, currency conversion layer, product matching logic, alerting, or dashboards. Those downstream choices are intentionally left to the user.

## Why fork this instead of writing one-off scripts?

Use Retail Scrapers when you want a reusable scraping foundation instead of a pile of
retailer-specific scripts that slowly drift apart.

| One-off scraper | Retail Scrapers |
|---|---|
| Hidden assumptions in each script | Shared records, validation, runtime options, and CLI behavior |
| Live websites hit from every test | Offline fixture tests first; live smoke checks are manual |
| Hard to tell partial failure from success | Strict mode fails when output is incomplete |
| Data storage mixed into extraction | Extraction-only package; your pipeline owns storage and matching |
| New retailer starts from a blank file | `retail-scrape scaffold --with-fixtures` creates the adapter path |

Good fit for:

- Forks that need catalog or price data from multiple public retail websites.
- Teams building their own price-history, alerting, matching, or analytics layer.
- Developers who want a tested adapter pattern for real-world ecommerce pages.

Not a fit for:

- Scraping private, logged-in, or personal data.
- High-volume crawling without reviewing the target site's acceptable-use rules.
- A turnkey dashboard or database product.

## 30-second demo

```bash
python -m pip install -e .
python -m playwright install chromium

retail-scrape catalog \
  --channel elkjop-no \
  --max-items 3 \
  --no-strict \
  --output output/elkjop.jsonl
```

Example output:

```json
{"channel":"elkjop-no","country":"NO","sku":"123456","brand":"Example","title":"Example 55 inch 4K TV","url":"https://www.example.com/product/123456","price":7990.0,"currency":"NOK","availability":"in_stock"}
```

Want the whole path at a glance? Open the [project showcase](docs/showcase.md) to see
how to run a channel, scaffold a new adapter, and connect the output downstream.

## Why this exists

Most scraper examples stop at "grab a page and parse some text." Real retail websites need a stronger pattern:

- API-first extraction when the frontend already calls a structured endpoint.
- Browser fallback for pages that require rendering or session setup.
- Strict completeness checks so a half-scraped catalog does not look successful.
- Channel isolation so one retailer change does not break every other adapter.
- No bundled user data, cookies, accounts, or private product mappings.

## Supported channels

For maintenance details, see [Channel health](docs/channel-health.md), or run:

```bash
retail-scrape health
retail-scrape health --format markdown
```

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

Inspect output contracts:

```bash
retail-scrape schema
retail-scrape schema catalog --format markdown
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

## Run on GitHub Actions

Forks can start from the copy-paste workflow in
[`examples/github-actions/scheduled-scrape.yml`](examples/github-actions/scheduled-scrape.yml).
It supports manual catalog runs, manual price runs, and a small scheduled smoke run that
uploads output as a GitHub Actions artifact.

See [Run scrapers on GitHub Actions](docs/automation.md) for setup notes and responsible
automation boundaries.

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

## Fork-friendly adapter design

Want to add another retailer? Start here:

```bash
retail-scrape scaffold example-shop-us \
  --display-name "Example Shop US" \
  --country US \
  --with-fixtures
```

This creates a starter adapter package, a matching identity test, and optional sanitized fixture-test skeletons, so a fork can focus on extraction logic instead of boilerplate.

- [Architecture](docs/architecture.md)
- [Adding a channel](docs/add-channel.md)
- [90-second new channel demo](docs/new-channel-demo.md)
- [API discovery playbook](docs/api-discovery-playbook.md)
- [Channel health](docs/channel-health.md)
- [Downstream usage](docs/downstream-usage.md)
- [GitHub Actions automation](docs/automation.md)
- [Project showcase](docs/showcase.md)
- [Roadmap](ROADMAP.md)
- [Example output](examples/output.example.jsonl)

Each retailer lives in its own adapter package under `src/retail_scrapers/adapters/`. Parser behavior should be covered by offline tests; live website checks belong in the manual smoke workflow.

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

Before running a live scrape, check your local environment:

```bash
retail-scrape doctor
```

## License

MIT
