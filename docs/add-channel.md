# Adding a channel

## 1. Confirm the data source

Check sources in this order:

1. JSON-LD or product metadata already embedded in the page.
2. REST, GraphQL, tRPC, search, or autocomplete APIs visible in the browser Network panel.
3. Server-rendered HTML.
4. Playwright-rendered pages only when JavaScript execution is necessary.

Do not start by guessing prices from visible text. Machine-readable fields are usually more stable and make it easier to separate current price, previous price, bundle price, and installment text.

## 2. Create an adapter

Add a new adapter package:

```text
src/retail_scrapers/adapters/<channel-id>/
├─ __init__.py
└─ adapter.py
```

Implement the two `ChannelAdapter` methods:

- `scrape_catalog`
- `scrape_prices`

Then register the adapter in `registry.py`.

## 3. Define completeness checks

If the source exposes total count or page count, cross-check it:

- The declared total must stay stable across pages.
- The final unique SKU count must match the source total.
- SKUs or URLs must not repeat across pages.
- Returned brand and year fields must match the filters when those filters are used.

If the website does not expose total count, document the limitation and keep at least non-empty, duplicate, and price-success-rate checks.

## 4. Add offline tests

Unit tests should not depend on live retail websites. Add minimal sanitized fixtures that test:

- Field parsing.
- Price and currency parsing.
- Pagination and duplicate detection.
- Empty and malformed responses.

Live website checks should live in the manual smoke workflow so every pull request does not hit retailer websites.

## 5. Run pre-release checks

```bash
ruff check .
pytest
mypy src/retail_scrapers
python -m pip wheel . --no-deps --wheel-dir dist
python -m retail_scrapers channels
```

Before committing, confirm that you did not add:

- Scraped results.
- Cookies, tokens, accounts, or proxy credentials.
- Personal paths or internal domains.
- User-specific product mappings or master data.
