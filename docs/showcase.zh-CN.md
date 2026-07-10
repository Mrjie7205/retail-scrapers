# 项目橱窗

理解 Retail Scrapers 最简单的方式，是看三条很短的使用路径：**跑起来、扩渠道、接下游**。下面只使用公开页面和合成示例数据。

## 1. 跑起来

第一次安装项目和浏览器后，先抓一个小规模 catalog 样本：

```bash
python -m pip install -e .
python -m playwright install chromium

retail-scrape catalog \
  --channel elkjop-no \
  --max-items 3 \
  --no-strict \
  --output output/elkjop.jsonl
```

输出是逐行 JSON，可以直接交给数据库、Pandas、对象存储或其他数据流水线：

```json
{"channel":"elkjop-no","country":"NO","sku":"demo-1001","brand":"Example","title":"Example Vision 55 inch 4K TV","url":"https://www.example.com/product/demo-1001","price":7990.0,"currency":"NOK","availability":"in_stock","model":"VISION55","model_year":2026,"size_inch":55.0,"scraped_at":"2026-01-01T00:00:00Z","metadata":{"source":"synthetic-example"}}
```

如果想定时运行，把
[`examples/github-actions/scheduled-scrape.yml`](../examples/github-actions/scheduled-scrape.yml)
复制到 fork 仓库的 `.github/workflows/retail-scrape.yml`。它支持手动 catalog、手动价格抓取和小规模每日 smoke run，结果会上传为 `retail-scrape-output-*` artifact。

## 2. 扩渠道

增加新零售商时，不需要手工复制已有渠道，先生成一套完整骨架：

```bash
retail-scrape scaffold example-shop-us \
  --display-name "Example Shop US" \
  --country US \
  --with-fixtures
```

命令会创建：

```text
src/retail_scrapers/adapters/example_shop_us/
tests/test_example_shop_us_adapter.py
tests/fixtures/example_shop_us/catalog.html
tests/fixtures/example_shop_us/product.html
```

命令还会打印 registry 配置和下一步可运行的命令。完整贡献路径见 [90 秒新增渠道 demo](新增渠道demo.md)。

## 3. 接下游

不读源代码，也可以直接查看公开的数据契约：

```bash
retail-scrape schema catalog --format markdown
```

Catalog 记录统一提供 `channel`、`country`、`sku`、`url`、`price`、`currency`、`scraped_at` 等跨渠道字段。零售商特有的公开字段放进 `metadata`，这样下游代码既可以依赖统一结构，也不会丢失有用的来源信息。

CSV、JSONL、Python 和数据仓库的接入例子见 [下游使用方式](downstream-usage.zh-CN.md)。

## 渠道快照

| 渠道 | 市场 | Catalog | 价格 | 主要策略 |
|---|---|---:|---:|---|
| `amazon-de` | 德国 | 是 | 是 | Playwright 和配送地会话 |
| `boulanger-fr` | 法国 | 是 | 是 | HTML、品牌筛选、Schema.org 兜底 |
| `currys-gb` | 英国 | 是 | 是 | 独立页面会话和 Schema.org 兜底 |
| `elkjop-no` | 挪威 | 是 | 是 | Algolia catalog API、tRPC 价格 API、页面兜底 |

运行 `retail-scrape health --format markdown` 可以查看便于机器读取的维护说明。零售网站经常变化，渠道是否健康仍应以当前 live smoke run 为准。

## 项目有意保留的边界

仓库不内置数据库、dashboard、商品匹配、汇率转换、私有账号、Cookie 或真实抓取数据。它只负责提取；存储、匹配、分析和展示由使用者自己的应用决定。

请只访问公开信息，控制请求频率，并在自动化前确认目标网站条款、robots 规则和适用法律。
