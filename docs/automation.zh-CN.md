# 用 GitHub Actions 定时运行爬虫

Retail Scrapers 本身刻意保持无状态。这个包只负责提取记录；至于结果是作为 artifact 保存、提交到另一个仓库、写入数据库，还是进入数仓，都由使用者自己的 workflow 决定。

仓库里提供了一份可复制的 workflow 模板：

```text
examples/github-actions/scheduled-scrape.yml
```

## 快速配置

1. fork 本仓库，或者把这个包复制到你自己的爬虫仓库。
2. 将模板复制到 `.github/workflows/retail-scrape.yml`。
3. 打开 GitHub 的 Actions 页面，手动运行 `Retail Scrapers scheduled run`。
4. 在运行结果页面下载 `retail-scrape-output-*` artifact。
5. smoke run 成功后，再调整 cron、渠道、`max_items` 和严格模式。

模板里的首次定时任务故意保持很小：

```yaml
schedule:
  - cron: "17 5 * * *"
```

生产使用时，更推荐“小规模每日价格抓取 + 低频 catalog 抓取”的节奏。零售网站经常改版，小规模 smoke run 比一次性大规模失败更容易排查。

## 手动 catalog 抓取

在 workflow dispatch 表单里填写：

- `channel`：渠道 ID，比如 `elkjop-no`。
- `mode`：选择 `catalog`。
- `max_items`：先从 `20` 开始，确认成功后再提高。
- `no_strict`：探索阶段保持开启；当你明确期待完整输出时再关闭。

抓取结果会作为 GitHub Actions artifact 上传。

## 手动价格抓取

价格抓取需要准备一个 CSV 文件，至少包含：

```csv
id,url
product-1,https://www.example.com/product/1
product-2,https://www.example.com/product/2
```

然后运行 workflow：

- `mode`：选择 `prices`。
- `input_file`：填写你的 CSV 文件路径。

## 推荐的生产节奏

可以先按这个拆分开始：

- 每日价格 smoke：小 URL 清单，开启严格模式。
- 每周 catalog smoke：较小的 `max_items`，观察期间可关闭严格模式。
- 手动全量 catalog：只在确实需要刷新、并确认目标网站使用边界后运行。

除非你的项目明确要发布样例数据，否则不要把生成数据放进 scraper 包本身。artifact 是一个更安全的默认选择：它能证明 workflow 跑过，又不会把工具仓库变成数据仓库。

## 自动化使用边界

- 控制请求量。
- 尊重目标网站的服务条款、robots 规则和适用法律。
- 不抓取需要登录或私有授权的数据。
- 不把 cookie 或凭据写进仓库。
- 如果要上传到下游系统，用 GitHub Secrets 管理 token。
