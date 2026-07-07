# Security

[中文文档](SECURITY.zh-CN.md)

Please do not post accounts, cookies, API keys, proxy credentials, or page samples containing personal information in public issues.

Retail Scrapers is intended only for public product information that does not require login. If an adapter unexpectedly accesses authenticated or restricted data, stop running it and report the issue without including sensitive content.

Short-lived session credentials must be acquired at runtime and kept in memory. They must not be written to logs, fixtures, or the repository.
