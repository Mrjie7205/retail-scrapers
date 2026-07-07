# Run scrapers on GitHub Actions

Retail Scrapers is intentionally stateless. The package extracts records; your workflow decides whether to keep them as artifacts, commit them to another repository, load them into a database, or send them to a warehouse.

This repository includes a copy-paste workflow template:

```text
examples/github-actions/scheduled-scrape.yml
```

## Quick setup

1. Fork this repository, or copy the package into your own scraper repository.
2. Copy the template to `.github/workflows/retail-scrape.yml`.
3. Open the Actions tab and run `Retail Scrapers scheduled run` manually.
4. Download the `retail-scrape-output-*` artifact from the run summary.
5. Tune the cron schedule, channel, `max_items`, and strictness once the smoke run works.

The template keeps the first scheduled run intentionally small:

```yaml
schedule:
  - cron: "17 5 * * *"
```

For production, prefer a small daily price run and a less frequent catalog run. Retail sites change frequently, and a compact smoke run is easier to debug than a large silent failure.

## Manual catalog run

Use the workflow dispatch form:

- `channel`: channel ID such as `elkjop-no`.
- `mode`: `catalog`.
- `max_items`: start with `20`; raise it only after a successful smoke test.
- `no_strict`: keep enabled for exploration, disable when you expect complete output.

The output is uploaded as a GitHub Actions artifact.

## Manual price run

For price extraction, commit or generate a CSV file with at least:

```csv
id,url
product-1,https://www.example.com/product/1
product-2,https://www.example.com/product/2
```

Then run the workflow with:

- `mode`: `prices`.
- `input_file`: path to your CSV file.

## Recommended production pattern

Start with this split:

- Daily price smoke: small list, strict mode on.
- Weekly catalog smoke: small `max_items`, strict mode off while you monitor drift.
- Manual full catalog: run only when you need a refresh and have checked the target site's acceptable use rules.

Keep generated data outside the scraper package unless your project intentionally publishes sample data. Artifacts are a safe default because they prove the workflow ran without turning the scraper repository into a data warehouse.

## Responsible automation

- Keep request volume low.
- Respect each target site's terms, robots rules, and applicable laws.
- Do not scrape logged-in or private data.
- Do not store cookies or credentials in the repository.
- Use GitHub Secrets for any downstream upload token.
