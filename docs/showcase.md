# Project showcase

Retail Scrapers is easiest to understand as three small loops: **run it, extend it,
connect it**. The examples below use public pages and synthetic output only.

## 1. Run it

Install the package and browser once, then request a small catalog sample:

```bash
python -m pip install -e .
python -m playwright install chromium

retail-scrape catalog \
  --channel elkjop-no \
  --max-items 3 \
  --no-strict \
  --output output/elkjop.jsonl
```

The output is newline-delimited JSON that can go directly into a database, data
frame, object store, or another pipeline:

```json
{"channel":"elkjop-no","country":"NO","sku":"demo-1001","brand":"Example","title":"Example Vision 55 inch 4K TV","url":"https://www.example.com/product/demo-1001","price":7990.0,"currency":"NOK","availability":"in_stock","model":"VISION55","model_year":2026,"size_inch":55.0,"scraped_at":"2026-01-01T00:00:00Z","metadata":{"source":"synthetic-example"}}
```

For unattended smoke runs, copy
[`examples/github-actions/scheduled-scrape.yml`](../examples/github-actions/scheduled-scrape.yml)
to `.github/workflows/retail-scrape.yml` in your fork. It supports manual catalog and
price runs, plus a small daily smoke run. Results are uploaded as a
`retail-scrape-output-*` artifact.

## 2. Extend it

Generate a complete adapter starting point instead of copying an existing channel by
hand:

```bash
retail-scrape scaffold example-shop-us \
  --display-name "Example Shop US" \
  --country US \
  --with-fixtures
```

The command creates:

```text
src/retail_scrapers/adapters/example_shop_us/
tests/test_example_shop_us_adapter.py
tests/fixtures/example_shop_us/catalog.html
tests/fixtures/example_shop_us/product.html
```

It also prints the registry entry and the next commands to run. Follow the
[90-second new channel demo](new-channel-demo.md) for the complete contributor path.

## 3. Connect it

Inspect the public output contract without reading the package source:

```bash
retail-scrape schema catalog --format markdown
```

Catalog records expose stable cross-channel fields such as `channel`, `country`,
`sku`, `url`, `price`, `currency`, and `scraped_at`. Retailer-specific public fields
stay inside `metadata`, so downstream code can depend on the common contract while
still retaining useful source details.

See [Downstream usage](downstream-usage.md) for CSV, JSONL, Python, and warehouse
integration examples.

## Channel snapshot

| Channel | Market | Catalog path | Price path | Primary strategy |
|---|---|---:|---:|---|
| `amazon-de` | Germany | Yes | Yes | Playwright and delivery-location session |
| `boulanger-fr` | France | Yes | Yes | HTML, brand facets, Schema.org fallback |
| `currys-gb` | United Kingdom | Yes | Yes | Isolated page sessions and Schema.org fallback |
| `elkjop-no` | Norway | Yes | Yes | Algolia catalog API, tRPC price API, page fallback |

Run `retail-scrape health --format markdown` for machine-readable maintenance notes.
Because retail sites change, live health should always be confirmed with a current
smoke run.

## Deliberate boundaries

This repository does not bundle a database, dashboard, product matching, currency
conversion, private accounts, cookies, or real scraped datasets. It is an extraction
toolkit: your application owns storage, matching, analytics, and presentation.

Use it only for public information, keep request rates reasonable, and review the
target website's terms, robots rules, and applicable law before automation.
