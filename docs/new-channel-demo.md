# 90-second new channel demo

This walkthrough shows the contribution path for a fork: generate a channel adapter, get fixture-test skeletons, register the adapter, and run focused tests.

It is intentionally small. Real adapters still need channel-specific API discovery, responsible request limits, and sanitized fixtures from public pages.

## 1. Generate the adapter

```bash
retail-scrape scaffold example-shop-us \
  --display-name "Example Shop US" \
  --country US \
  --with-fixtures
```

The command prints the generated files plus next-step instructions:

```json
{
  "created": [
    "src/retail_scrapers/adapters/example_shop_us/__init__.py",
    "src/retail_scrapers/adapters/example_shop_us/adapter.py",
    "tests/test_example_shop_us_adapter.py",
    "tests/fixtures/example_shop_us/catalog.sample.json",
    "tests/fixtures/example_shop_us/price.sample.json",
    "tests/test_example_shop_us_fixtures.py"
  ],
  "instructions": {
    "adapter_class": "ExampleShopUsAdapter",
    "registry_import": "from .adapters.example_shop_us import ExampleShopUsAdapter",
    "registry_entry": "ExampleShopUsAdapter(),"
  }
}
```

## 2. Register the adapter

Open `src/retail_scrapers/registry.py`.

Add the import:

```python
from .adapters.example_shop_us import ExampleShopUsAdapter
```

Add the adapter instance:

```python
ADAPTERS = {
    adapter.channel_id: adapter
    for adapter in (
        AmazonDeAdapter(),
        BoulangerFrAdapter(),
        CurrysGbAdapter(),
        ElkjopNoAdapter(),
        ExampleShopUsAdapter(),
    )
}
```

Then confirm the channel is visible:

```bash
retail-scrape channels
```

## 3. Replace the placeholders

The generated adapter deliberately returns empty lists. Replace those placeholders with extraction logic:

- Start from public JSON-LD or frontend APIs.
- Keep catalog extraction and price extraction independent.
- Return failed `PriceRecord` rows for individual product failures instead of crashing a full price run.
- Keep adapter-specific public details inside `metadata`.

If you used `--with-fixtures`, replace `example.com` fixture data with tiny sanitized samples from public responses.

## 4. Run focused checks

```bash
pytest tests/test_example_shop_us_adapter.py
pytest tests/test_example_shop_us_fixtures.py
ruff check src/retail_scrapers/adapters/example_shop_us tests/test_example_shop_us_*.py
```

Before opening a pull request, run the full project checks:

```bash
ruff check .
pytest
mypy src/retail_scrapers
python -m pip wheel . --no-deps --wheel-dir dist
```

This path gives contributors a clean fork loop: scaffold, implement, test offline, then run live smoke checks manually.
