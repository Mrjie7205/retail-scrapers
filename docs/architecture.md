# Architecture

## Project boundary

Retail Scrapers is an extraction layer, not a full price-monitoring platform. The core project does four things:

1. Accept a channel and filter options.
2. Call a channel adapter to collect public retail product data.
3. Validate that the result is complete, reasonable, and traceable.
4. Return unified catalog or price records as Python objects, JSONL, or CSV.

The project does not provide a database, product master data, currency conversion, alerting, frontend dashboards, or private data synchronization.

## Runtime flow

```text
CLI / Python API
      ↓
registry selects a channel adapter
      ↓
adapter chooses API, HTTP, or Playwright
      ↓
unified CatalogRecord / PriceRecord
      ↓
validation in strict mode
      ↓
CSV / JSONL / Python objects
```

You can inspect the output contract with:

```bash
retail-scrape schema
retail-scrape schema catalog --format markdown
```

## Directory responsibilities

- `core/`: shared browser and price-parsing utilities.
- `adapters/`: retailer-specific requests, pagination, and field mapping.
- `models.py`: stable public output contracts.
- `validation.py`: channel-independent quality checks.
- `runner.py`: Python API and runtime lifecycle.
- `cli.py`: command-line arguments; it should not contain scraping logic.

## Design principles

- Prefer API-first extraction, but assume endpoints may change.
- Keep each retailer isolated in its own adapter.
- Fail with a non-zero exit status when strict-mode data is incomplete.
- Let user data flow from input to output only; do not write it into the repository.
- Channel constants may describe public websites, but must not include user-specific business rules.

## Runtime tuning

The CLI exposes shared runtime controls:

- `--timeout-ms`: request or page-navigation timeout in milliseconds.
- `--retries`: number of retry attempts after the first request.
- `--delay-seconds`: polite delay between retries, pages, or sequential product visits.

Adapters should use these options instead of hardcoded timing values whenever practical. Defaults are intentionally conservative enough for local use and short GitHub Actions smoke tests.
