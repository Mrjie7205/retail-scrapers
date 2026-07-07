# Price demo

Price extraction starts from a user-provided URL list.

```bash
retail-scrape prices \
  --channel currys-gb \
  --input examples/products.example.csv \
  --output output/prices.jsonl
```

Input files must contain at least:

```csv
id,url
demo-1,https://www.example.com/product/demo-1
demo-2,https://www.example.com/product/demo-2
```

Use `--min-success-rate` to decide how strict a price run should be. In strict mode, the command exits with a non-zero status if the success rate is too low.
