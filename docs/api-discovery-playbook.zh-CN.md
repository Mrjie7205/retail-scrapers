# API 发现手册

这份文档说明在写 parser 之前，如何优先寻找更稳定的零售网站数据源。它只面向无需登录的公开商品数据。

## 简短版本

建议按这个顺序检查：

1. 页面里的 JSON-LD 和内嵌初始化数据。
2. DevTools Network 里的前端 API 请求。
3. 在浏览器外复现最小可用请求。
4. 校验总量、分页、ID、价格和筛选条件。
5. 最后再写 adapter。

如果一上来就抓可见文本，通常会被布局改版、促销横幅和 A/B test 牵着走。API-first 的本质不是魔法，而是耐心找到网站前端自己正在使用的数据源。

## 1. 从商品页开始

打开商品页，优先检查：

- `<script type="application/ld+json">`
- `window.__INITIAL_STATE__`、`__NEXT_DATA__` 或类似 hydration 数据
- SKU、标题、品牌、价格、币种、库存
- canonical URL 和稳定商品 ID

如果 JSON-LD 里已经有价格和币种，应优先作为价格 parser。可见文本 selector 更适合作为兜底。

## 2. 检查 Network 请求

打开浏览器 DevTools，刷新商品页或类目页。

常用过滤关键词：

- `Fetch/XHR`
- `json`
- `graphql`
- `trpc`
- `search`
- `algolia`
- `product`
- `price`
- `availability`

重点找返回结构化商品数组的请求。强信号包括：

- 总量或 `nbHits`
- 页码或 cursor
- SKU 或商品 ID
- 品牌和标题
- 原生价格和币种
- 库存或可售状态
- 品牌、类目、年份、尺寸等筛选字段

## 3. 复现请求

写 adapter 前，先用最小必要 headers 复现请求：

- URL
- method
- query string 或 JSON body
- 前端公开暴露的 API key
- 必要时加 `accept`、`content-type`、`referer`、语言 headers

不要复制 Cookie，除非数据本身是公开的，并且 Cookie 只是匿名短会话。不要把 Cookie 写进 fixture 或日志。

## 4. 校验筛选正确性

目录抓取需要逐个测试筛选条件：

- 只筛类目
- 品牌筛选
- 年份或尺寸筛选
- 第 1 页和第 2 页
- 最后一页

对比：

- 来源声明总量 vs 最终唯一记录数
- SKU 或 URL 是否重复
- 请求筛选条件 vs 返回字段
- 分页过程中的总量是否稳定

如果来源说有 247 个商品，而 adapter 只返回 48 个，严格模式应该失败。

## 5. 选择 adapter 策略

| 数据源形态 | 优先策略 |
|---|---|
| 商品页 JSON-LD | HTML 请求 + schema parser |
| 公开 REST 或 tRPC 接口 | Playwright request context 或 HTTP client |
| Algolia 或搜索 API | 发现签名/公开 key + 分页 API |
| 服务端渲染类目 HTML | HTML parser + 商品卡局部 selector |
| 必须执行 JavaScript | Playwright 页面兜底 |

Playwright 适合做会话设置和兜底，但如果有稳定 API，不应默认用浏览器硬爬。

## 6. 增加离线测试

fixture 应尽量小且脱敏：

- 一个商品卡
- 一个商品 JSON 响应
- 一个异常响应
- 一个重复或空响应

不要提交真实抓取数据集、Cookie、账号标识、代理凭据或个人数据。

## 7. 记录风险

每个 adapter 都应说明自己的假设：

- 是否能做总量校验？
- API key 是公开还是短期签名？
- 价格是否为原生币种？
- 来源是否提供库存状态？
- API 失败时有什么兜底？

好的 adapter 应该很“无聊”：来源改版时大声失败，而不是安静地返回半量数据。
