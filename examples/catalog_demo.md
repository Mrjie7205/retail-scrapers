# Catalog demo

This example shows the intended shape of a small catalog extraction run.

```bash
retail-scrape catalog \
  --channel elkjop-no \
  --max-items 3 \
  --no-strict \
  --output examples/output.example.jsonl
```

The sample output in this repository is synthetic. It demonstrates the schema without storing real scraped data.

Key fields:

- `channel`: adapter ID.
- `country`: market code.
- `sku`: retailer SKU or stable product identifier.
- `brand`: retailer-provided brand.
- `title`: product title.
- `url`: product page URL.
- `price`: native current price when available.
- `currency`: retailer-native currency.
- `availability`: coarse availability status when available.
- `metadata`: optional public auxiliary fields.
