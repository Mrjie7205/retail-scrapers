# 90 秒新增渠道 demo

这份 walkthrough 展示 fork 用户的贡献路径：生成渠道 adapter、得到 fixture 测试骨架、注册 adapter，并运行聚焦测试。

它刻意保持很小。真实 adapter 仍然需要针对具体渠道做 API 发现、控制请求频率，并使用来自公开页面的最小脱敏 fixture。

## 一、生成 adapter

```bash
retail-scrape scaffold example-shop-us \
  --display-name "Example Shop US" \
  --country US \
  --with-fixtures
```

命令会输出生成的文件和下一步说明：

```json
{
  "created": [
    "src/retail_scrapers/adapters/example_shop_us/__init__.py",
    "src/retail_scrapers/adapters/example_shop_us/adapter.py",
    "tests/test_example_shop_us_adapter.py",
    "tests/fixtures/example_shop_us/catalog.sample.json",
    "tests/fixtures/example_shop_us/price.sample.json",
    "tests/test_example_shop_us_fixtures.py"
  ],
  "instructions": {
    "adapter_class": "ExampleShopUsAdapter",
    "registry_import": "from .adapters.example_shop_us import ExampleShopUsAdapter",
    "registry_entry": "ExampleShopUsAdapter(),"
  }
}
```

## 二、注册 adapter

打开 `src/retail_scrapers/registry.py`。

加入 import：

```python
from .adapters.example_shop_us import ExampleShopUsAdapter
```

加入 adapter 实例：

```python
ADAPTERS = {
    adapter.channel_id: adapter
    for adapter in (
        AmazonDeAdapter(),
        BoulangerFrAdapter(),
        CurrysGbAdapter(),
        ElkjopNoAdapter(),
        ExampleShopUsAdapter(),
    )
}
```

然后确认渠道能被列出：

```bash
retail-scrape channels
```

## 三、替换占位逻辑

生成的 adapter 会故意返回空列表。接下来要把占位逻辑替换成真实提取逻辑：

- 优先从公开 JSON-LD 或前端 API 开始。
- catalog 抓取和价格抓取保持独立。
- 单个商品价格失败时，返回失败状态的 `PriceRecord`，不要让整次价格任务崩掉。
- 渠道特定的公开辅助信息放进 `metadata`。

如果使用了 `--with-fixtures`，请把 `example.com` 合成数据替换为公开响应里的最小脱敏样本。

## 四、运行聚焦检查

```bash
pytest tests/test_example_shop_us_adapter.py
pytest tests/test_example_shop_us_fixtures.py
ruff check src/retail_scrapers/adapters/example_shop_us tests/test_example_shop_us_*.py
```

提交 PR 前，再跑完整项目检查：

```bash
ruff check .
pytest
mypy src/retail_scrapers
python -m pip wheel . --no-deps --wheel-dir dist
```

这条路径给贡献者一个清晰的 fork 循环：生成骨架、实现逻辑、离线测试，再手动运行 live smoke。
