# Channel health

Retail websites change frequently. This page is a capability and maintenance overview, not a permanent guarantee that every live website is reachable at this moment.

For the latest live check, run the manual GitHub Actions workflow:

```text
Actions → Manual live smoke test → Run workflow → channel=all
```

You can also inspect the built-in metadata locally:

```bash
retail-scrape health
retail-scrape health --format markdown
```

## Built-in channels

| Channel | Market | Catalog strategy | Price strategy | Validation | Maintenance risk |
|---|---|---|---|---|---|
| `amazon-de` | Germany | Playwright search pages with delivery-location session | Product page schema/selector parsing with native EUR validation | Filters obvious non-TV results; validates EUR prices | High: search-page layout and anti-automation behavior may drift |
| `boulanger-fr` | France | Server HTML parsing with brand facets | HTML Schema.org first, Playwright page fallback | Card-level price parsing; native EUR price checks | Medium: product card markup may change |
| `currys-gb` | United Kingdom | Isolated Playwright sessions for paginated category pages | Product page Schema.org first, selector fallback | Total-count validation when running an unfiltered full catalog | High: category pages can be sensitive to session and layout changes |
| `elkjop-no` | Norway | Algolia catalog API with signed public frontend key | tRPC dynamic product data API, page fallback | Total/page/SKU/year checks for strict catalog extraction | Medium: frontend API contracts or signed-key endpoint may change |

## How to interpret health

- `CI` proves the package imports, unit tests pass, type checks pass, and distributions build.
- `Manual live smoke test` proves that a tiny sample of a live website is currently reachable from GitHub Actions.
- A successful smoke test does not prove a full catalog is complete.
- A failed smoke test may mean the website changed, GitHub Actions is blocked, or a transient network issue occurred.

For a real production workflow, combine:

1. Offline parser fixtures.
2. Manual live smoke tests.
3. Strict full-catalog validation when the source exposes total counts.
4. A downstream alert when success rate or record count changes unexpectedly.
