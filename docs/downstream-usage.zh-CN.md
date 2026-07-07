# 下游使用方式

Retail Scrapers 输出简单的 JSONL 或 CSV 记录，后续如何存储、匹配、 enrich 或可视化由使用者决定。

查看公共数据契约：

```bash
retail-scrape schema
retail-scrape schema catalog --format markdown
retail-scrape schema price --format markdown
```

## 用 pandas 读取 JSONL

```python
import pandas as pd

df = pd.read_json("output/elkjop.jsonl", lines=True)
print(df[["channel", "sku", "title", "price", "currency"]].head())
```

## 用 pandas 读取 CSV

```python
import pandas as pd

df = pd.read_csv("output/amazon.csv")
df["scraped_at"] = pd.to_datetime(df["scraped_at"], utc=True)
```

## 存入 SQLite

```python
import sqlite3
import pandas as pd

df = pd.read_json("output/prices.jsonl", lines=True)

with sqlite3.connect("retail_prices.sqlite") as con:
    df.to_sql("prices", con, if_exists="append", index=False)
```

## 用 DuckDB 查询

```sql
SELECT channel, currency, count(*) AS rows, avg(price) AS avg_price
FROM read_json_auto('output/*.jsonl')
WHERE price IS NOT NULL
GROUP BY channel, currency
ORDER BY rows DESC;
```

## 建议的下游边界

以下逻辑建议放在 scraper 包之外：

- 匹配内部商品主数据。
- 汇率换算。
- 长期价格历史。
- 告警和看板。
- 业务特定筛选规则。

这个边界能让 adapter 更容易复用。fork 用户可以改变下游存储方式，而不需要改提取逻辑。
