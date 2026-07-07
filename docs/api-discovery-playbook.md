# API discovery playbook

This guide explains how to look for stable retail data sources before writing a parser. It is meant for public product data that does not require login.

## The short version

Use this order:

1. Inspect JSON-LD and embedded page data.
2. Watch frontend API calls in DevTools.
3. Reproduce the smallest useful request outside the browser.
4. Validate totals, pages, IDs, prices, and filters.
5. Only then write the adapter.

If you start by scraping visible text, you usually inherit every layout change, promo banner, and A/B test. API-first extraction is not magic; it is just being patient enough to find the data source the website already uses.

## 1. Start with the product page

Open a product page and check:

- `<script type="application/ld+json">`
- `window.__INITIAL_STATE__`, `__NEXT_DATA__`, or similar hydration payloads
- product SKU, title, brand, price, currency, availability
- canonical URL and stable product IDs

If JSON-LD has price and currency, use it as the first price parser. Keep selector-based text parsing as a fallback.

## 2. Inspect Network requests

Open browser DevTools and reload the page or category listing.

Useful filters:

- `Fetch/XHR`
- `json`
- `graphql`
- `trpc`
- `search`
- `algolia`
- `product`
- `price`
- `availability`

Look for requests that return structured product arrays. Strong signals include:

- total count or `nbHits`
- page number or cursor
- SKU or product ID
- brand and title
- native price and currency
- availability or sellability
- filter values such as brand, category, year, size

## 3. Reproduce the request

Before writing an adapter, reproduce the request with the smallest required headers:

- URL
- method
- query string or JSON body
- public API key if the frontend exposes one
- `accept`, `content-type`, `referer`, and language headers when needed

Avoid copying cookies unless the data is public and the cookie is only a short-lived anonymous session. Do not persist cookies in fixtures or logs.

## 4. Test filter correctness

For catalog extraction, test one filter at a time:

- category only
- brand filter
- year or size filter
- page 1 and page 2
- last page

Compare:

- declared total count vs collected unique records
- duplicate SKU or URL
- requested filters vs returned fields
- cross-page consistency

Strict mode should fail if the source says there are 247 products and the adapter only returns 48.

## 5. Choose the adapter strategy

| Source shape | Preferred strategy |
|---|---|
| JSON-LD on product page | HTML request + schema parser |
| Public REST or tRPC endpoint | Playwright request context or HTTP client |
| Algolia or search API | signed/public key discovery + paginated API calls |
| Server-rendered category HTML | HTML parser with card-level selectors |
| JavaScript-only rendering | Playwright page fallback |

Use Playwright for setup and fallback, but do not default to it when a stable API is available.

## 6. Add offline tests

Keep fixtures tiny and sanitized:

- one product card
- one product JSON response
- one malformed response
- one duplicate or empty response

Do not commit real scraped datasets, cookies, account identifiers, proxy credentials, or personal data.

## 7. Document the risk

Each adapter should make its assumptions visible:

- Is total-count validation available?
- Is the API key public or short-lived?
- Is price native currency only?
- Does the source include availability?
- Which fallback exists if the API fails?

Good adapters are boring: they fail loudly when the source changes, instead of silently returning partial data.
