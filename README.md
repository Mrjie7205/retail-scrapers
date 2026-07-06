# Retail Scrapers

Retail Scrapers 是一个面向真实零售网站的 Python 抓取工具箱。它提供可直接运行的渠道适配器，
负责提取商品目录和当前价格，并把结果输出为统一的 CSV 或 JSONL。

项目只负责“可靠地拿到结构化数据”。数据库、价格趋势、汇率换算、商品匹配、告警和可视化由使用者
自行决定。

## 核心特点

- API 优先：优先复用零售网站前端公开调用的数据接口。
- 浏览器兜底：需要渲染页面时使用 Playwright。
- 渠道隔离：每个渠道是独立 adapter，共享请求、校验和输出能力。
- 严格检查：支持数量、分页、SKU 去重和价格任务成功率校验。
- 无内置数据：仓库不保存用户抓取结果、账号、Cookie 或业务映射表。

## 内置渠道

| 渠道 ID | 国家 | 目录 | 价格 | 主要策略 |
|---|---|---:|---:|---|
| `amazon-de` | 德国 | ✓ | ✓ | Playwright、配送地会话、EUR 校验 |
| `boulanger-fr` | 法国 | ✓ | ✓ | 品牌 facet、懒加载、Schema.org |
| `currys-gb` | 英国 | ✓ | ✓ | 独立分页会话、Schema.org |
| `elkjop-no` | 挪威 | ✓ | ✓ | Algolia 目录、tRPC 价格、页面兜底 |

网站会持续改版，因此 adapter 是否可用应以最近一次测试和运行日志为准。

## 安装

```bash
python -m pip install -e .
python -m playwright install chromium
```

开发环境：

```bash
python -m pip install -e ".[dev]"
```

## 命令行使用

查看支持的渠道：

```bash
retail-scrape channels
```

抓取 Elkjøp 指定年份的完整电视目录：

```bash
retail-scrape catalog \
  --channel elkjop-no \
  --year 2025 \
  --year 2026 \
  --output output/elkjop.jsonl
```

按品牌抓取 Amazon Germany 搜索目录：

```bash
retail-scrape catalog \
  --channel amazon-de \
  --brand Samsung \
  --brand Sony \
  --postal-code 10115 \
  --output output/amazon.csv \
  --format csv
```

按 URL 清单抓价格：

```bash
retail-scrape prices \
  --channel currys-gb \
  --input examples/products.example.csv \
  --output output/prices.jsonl
```

输入文件至少包含 `id` 和 `url`：

```csv
id,url
product-1,https://www.example.com/product/1
product-2,https://www.example.com/product/2
```

默认启用严格模式。价格成功率低于 80%，或支持总量校验的目录出现缺页时，命令返回非零退出码。
探索或排障时可使用 `--no-strict`。

## Python 使用

```python
from retail_scrapers import scrape_catalog

records = scrape_catalog(
    "elkjop-no",
    years=[2025, 2026],
)

for record in records:
    print(record.sku, record.price, record.currency)
```

异步应用可使用 `retail_scrapers.runner` 中的 `scrape_catalog_async` 和
`scrape_prices_async`。

## 输出原则

- 保留网站原始币种，不默认换算汇率。
- 不替用户匹配内部商品主数据。
- 不持久化 Cookie、会话或抓取结果。
- `metadata` 只保存渠道公开返回的辅助字段。

## 使用边界

使用者应自行确认目标网站的服务条款、robots 规则和所在地区法律要求。请控制请求频率，不访问需要
登录或授权的数据，不采集个人信息，也不要使用本项目破坏网站服务。

## 开发

```bash
ruff check .
pytest
mypy src/retail_scrapers
```

新增渠道请阅读 [新增渠道指南](docs/新增渠道.md)。整体设计见
[架构说明](docs/架构说明.md)。

## 许可证

MIT
