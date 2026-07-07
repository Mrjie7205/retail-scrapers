## Summary

What does this PR change?

## Type of change

- [ ] Adapter fix
- [ ] New channel adapter
- [ ] Parser fixture / test improvement
- [ ] Documentation
- [ ] CLI / shared runtime
- [ ] Maintenance / CI

## Checklist

- [ ] I did not commit scraped datasets, cookies, credentials, personal data, or private business mappings.
- [ ] I added or updated offline tests for parser behavior where relevant.
- [ ] I ran `ruff check .`.
- [ ] I ran `pytest`.
- [ ] I ran `mypy src/retail_scrapers`.
- [ ] I ran `python -m retail_scrapers doctor --skip-browser`.

## Adapter changes only

- [ ] The adapter keeps retailer-specific logic inside its own package.
- [ ] The adapter uses public, non-login product data only.
- [ ] The adapter documents its catalog and price strategy.
- [ ] Strict mode fails loudly on incomplete data when totals are available.

## Live website checks

If this touches a live adapter, note whether you ran the manual smoke workflow and what happened.
