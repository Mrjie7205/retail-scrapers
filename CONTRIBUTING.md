# Contributing

[中文文档](CONTRIBUTING.zh-CN.md)

Contributions are welcome, especially fixes for existing adapters and new public retail channels.

Before opening a pull request:

1. Open an issue describing the channel, market, catalog entry point, and proposed extraction strategy.
2. Keep retailer-specific logic inside a dedicated adapter.
3. Add offline fixture tests for parser behavior.
4. Do not commit scraped results, credentials, cookies, personal information, or internal business data.
5. Run `ruff check .`, `pytest`, and `mypy src/retail_scrapers`.
6. Run `python -m retail_scrapers doctor --skip-browser` before opening the PR.

Real retail websites may restrict automated access. Contributors are responsible for following the target site's terms and using reasonable request rates.
