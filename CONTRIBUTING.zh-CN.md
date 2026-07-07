# 贡献指南

[English version](CONTRIBUTING.md)

欢迎修复现有渠道或增加新的公开零售渠道。

提交 Pull Request 前请：

1. 先创建 Issue，说明渠道、国家/市场、目录入口和建议方案。
2. 将网站特定逻辑限制在独立 adapter 中。
3. 为解析逻辑添加离线 fixture 测试。
4. 不提交抓取结果、凭据、Cookie、个人信息或企业内部数据。
5. 运行 `ruff check .`、`pytest` 和 `mypy src/retail_scrapers`。
6. 提交 PR 前运行 `python -m retail_scrapers doctor --skip-browser`。

真实网站可能限制自动访问。贡献者需要遵守目标网站条款，并使用合理的请求频率。
