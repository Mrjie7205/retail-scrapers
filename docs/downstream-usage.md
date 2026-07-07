# Downstream usage

Retail Scrapers writes simple JSONL or CSV records so you can decide how to store, match, enrich, or visualize the data.

Inspect the public schema:

```bash
retail-scrape schema
retail-scrape schema catalog --format markdown
retail-scrape schema price --format markdown
```

## Load JSONL with pandas

```python
import pandas as pd

df = pd.read_json("output/elkjop.jsonl", lines=True)
print(df[["channel", "sku", "title", "price", "currency"]].head())
```

## Load CSV with pandas

```python
import pandas as pd

df = pd.read_csv("output/amazon.csv")
df["scraped_at"] = pd.to_datetime(df["scraped_at"], utc=True)
```

## Store records in SQLite

```python
import sqlite3
import pandas as pd

df = pd.read_json("output/prices.jsonl", lines=True)

with sqlite3.connect("retail_prices.sqlite") as con:
    df.to_sql("prices", con, if_exists="append", index=False)
```

## Query with DuckDB

```sql
SELECT channel, currency, count(*) AS rows, avg(price) AS avg_price
FROM read_json_auto('output/*.jsonl')
WHERE price IS NOT NULL
GROUP BY channel, currency
ORDER BY rows DESC;
```

## Suggested downstream boundaries

Keep these concerns outside the scraper package:

- Product matching to your internal master data.
- Currency conversion.
- Long-term price history.
- Alerts and dashboards.
- Business-specific filtering rules.

This boundary keeps adapters reusable. A fork can change downstream storage without changing extraction logic.
