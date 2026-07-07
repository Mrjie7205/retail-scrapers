# 渠道健康状态

零售网站会频繁改版。本页是能力和维护风险概览，不代表每个真实网站在任意时刻都一定可访问。

如需最新 live 检查，请手动运行 GitHub Actions：

```text
Actions → Manual live smoke test → Run workflow → channel=all
```

也可以在本地查看内置元数据：

```bash
retail-scrape health
retail-scrape health --format markdown
```

## 内置渠道

| 渠道 | 市场 | 目录策略 | 价格策略 | 校验 | 维护风险 |
|---|---|---|---|---|---|
| `amazon-de` | 德国 | Playwright 搜索页 + 配送地会话 | 商品页 schema/selector 解析 + 原生 EUR 校验 | 过滤明显非电视结果；校验 EUR 价格 | 高：搜索页布局和反自动化行为可能变化 |
| `boulanger-fr` | 法国 | 服务端 HTML + 品牌 facet | HTML Schema.org 优先，Playwright 页面兜底 | 商品卡局部价格解析；原生 EUR 校验 | 中：商品卡 markup 可能变化 |
| `currys-gb` | 英国 | 分页类目页使用隔离 Playwright 会话 | 商品页 Schema.org 优先，selector 兜底 | 非筛选全量目录可做总量校验 | 高：类目页可能受会话和布局变化影响 |
| `elkjop-no` | 挪威 | Algolia 目录 API + 前端签名 key | tRPC 动态商品价格 API，页面兜底 | 严格模式校验总量、分页、SKU、年份 | 中：前端 API 契约或签名 key endpoint 可能变化 |

## 如何理解健康状态

- `CI` 证明包能导入、单元测试通过、类型检查通过、发布包能构建。
- `Manual live smoke test` 证明 GitHub Actions 当前能从真实网站抓到少量样本。
- smoke test 成功不等于全量目录一定完整。
- smoke test 失败可能是网站改版、GitHub Actions 被拦、或临时网络问题。

真实生产流程建议组合：

1. 离线 parser fixture。
2. 手动 live smoke test。
3. 来源提供总量时，使用严格全量校验。
4. 下游对成功率或记录数异常做告警。
