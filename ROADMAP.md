# Roadmap

Retail Scrapers is intentionally small: it should stay focused on reliable extraction, clean adapter boundaries, and useful output contracts.

## Near term

- Publish the first PyPI release.
- Add a generated channel health table that can ingest manual smoke-test artifacts.
- Add more offline parser fixtures for each built-in adapter.
- Expand the adapter scaffold command with optional parser helper templates.
- Add more first-run diagnostics to `retail-scrape doctor`.
- Improve examples for catalog extraction, price extraction, and downstream storage.

## Adapter quality

- Prefer public frontend APIs where available.
- Keep Playwright usage as a fallback, not the default for every website.
- Validate totals, page counts, duplicates, and success rates whenever possible.
- Keep retailer-specific assumptions inside the adapter package.

## Good first issues

- Add a minimal offline fixture test for one parser branch.
- Improve the API discovery playbook with more anonymized endpoint examples.
- Add a small example showing how to load JSONL output into pandas.
- Add a new retailer adapter proposal using the channel request template.

## Not in scope

- Storing long-term price history.
- Matching scraped products to private product master data.
- Currency conversion.
- Logged-in or authorization-only data.
- Personal data collection.
