"""Generate a starter adapter package for a new retail channel."""

from __future__ import annotations

import re
from pathlib import Path

CHANNEL_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def package_name(channel_id: str) -> str:
    channel = channel_id.strip().lower()
    if not CHANNEL_RE.fullmatch(channel):
        raise ValueError(
            "channel_id must use lowercase letters, digits, and hyphens, "
            "for example 'example-shop-us'"
        )
    return channel.replace("-", "_")


def class_name(channel_id: str) -> str:
    return "".join(part.capitalize() for part in package_name(channel_id).split("_")) + "Adapter"


def adapter_template(channel_id: str, display_name: str, country: str) -> str:
    klass = class_name(channel_id)
    return f'''"""Starter adapter for {display_name}."""

from __future__ import annotations

from collections.abc import Sequence

from ...core.browser import BrowserRuntime
from ...models import CatalogRecord, PriceRecord, PriceTarget
from ...options import CatalogOptions, PriceOptions
from ..base import ChannelAdapter


class {klass}(ChannelAdapter):
    channel_id = "{channel_id}"
    display_name = "{display_name}"
    country = "{country}"

    async def scrape_catalog(
        self,
        runtime: BrowserRuntime,
        options: CatalogOptions,
    ) -> Sequence[CatalogRecord]:
        # Start with public JSON-LD, frontend APIs, or server-rendered HTML.
        # Use Playwright only when rendering or session setup is required.
        _ = (runtime, options)
        return []

    async def scrape_prices(
        self,
        runtime: BrowserRuntime,
        targets: Sequence[PriceTarget],
        options: PriceOptions,
    ) -> Sequence[PriceRecord]:
        # Keep price extraction independent from catalog extraction.
        # Return failed PriceRecord rows instead of raising for individual products.
        _ = (runtime, targets, options)
        return []
'''


def init_template(channel_id: str) -> str:
    klass = class_name(channel_id)
    return f"""from .adapter import {klass}

__all__ = ["{klass}"]
"""


def test_template(channel_id: str) -> str:
    package = package_name(channel_id)
    klass = class_name(channel_id)
    return f"""from retail_scrapers.adapters.{package} import {klass}


def test_{package}_adapter_identity():
    adapter = {klass}()
    assert adapter.channel_id == "{channel_id}"
    assert adapter.supports_catalog is True
    assert adapter.supports_prices is True
"""


def fixture_catalog_template(channel_id: str) -> str:
    return f"""{{
  "channel": "{channel_id}",
  "items": [
    {{
      "sku": "demo-sku-1",
      "brand": "Example",
      "title": "Example 55 inch 4K TV",
      "url": "https://www.example.com/product/demo-sku-1",
      "price": 799.0,
      "currency": "EUR",
      "availability": "in_stock"
    }}
  ]
}}
"""


def fixture_price_template(channel_id: str) -> str:
    return f"""{{
  "channel": "{channel_id}",
  "sku": "demo-sku-1",
  "price": 799.0,
  "currency": "EUR",
  "availability": "in_stock"
}}
"""


def fixture_test_template(channel_id: str) -> str:
    package = package_name(channel_id)
    return f'''import json
from pathlib import Path


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "{package}"


def test_{package}_catalog_fixture_is_minimal_and_sanitized():
    payload = json.loads((FIXTURE_DIR / "catalog.sample.json").read_text(encoding="utf-8"))
    assert payload["channel"] == "{channel_id}"
    assert payload["items"][0]["sku"] == "demo-sku-1"
    assert "example.com" in payload["items"][0]["url"]


def test_{package}_price_fixture_is_minimal_and_sanitized():
    payload = json.loads((FIXTURE_DIR / "price.sample.json").read_text(encoding="utf-8"))
    assert payload["channel"] == "{channel_id}"
    assert payload["price"] > 0
    assert payload["currency"]
'''


def scaffold_instructions(channel_id: str) -> dict[str, str | list[str]]:
    """Return human-facing next steps for a newly generated adapter."""

    package = package_name(channel_id)
    klass = class_name(channel_id)
    return {
        "adapter_class": klass,
        "registry_import": f"from .adapters.{package} import {klass}",
        "registry_entry": f"{klass}(),",
        "next_steps": [
            "Implement scrape_catalog and scrape_prices in the generated adapter.",
            "Add the registry import and registry entry to src/retail_scrapers/registry.py.",
            f"Run pytest tests/test_{package}_adapter.py.",
            "Replace synthetic fixtures with small sanitized public samples "
            "if --with-fixtures was used.",
        ],
    }


def create_adapter_scaffold(
    channel_id: str,
    *,
    display_name: str | None = None,
    country: str = "XX",
    root: Path | None = None,
    with_fixtures: bool = False,
) -> list[Path]:
    channel = channel_id.strip().lower()
    package = package_name(channel)
    project_root = root or Path.cwd()
    adapter_dir = project_root / "src" / "retail_scrapers" / "adapters" / package
    test_path = project_root / "tests" / f"test_{package}_adapter.py"

    if adapter_dir.exists() or test_path.exists():
        raise FileExistsError(f"adapter scaffold already exists for {channel!r}")

    adapter_dir.mkdir(parents=True, exist_ok=False)
    name = display_name or channel.replace("-", " ").title()
    files = {
        adapter_dir / "__init__.py": init_template(channel),
        adapter_dir / "adapter.py": adapter_template(channel, name, country.upper()),
        test_path: test_template(channel),
    }
    if with_fixtures:
        fixture_dir = project_root / "tests" / "fixtures" / package
        files.update(
            {
                fixture_dir / "catalog.sample.json": fixture_catalog_template(channel),
                fixture_dir / "price.sample.json": fixture_price_template(channel),
                project_root / "tests" / f"test_{package}_fixtures.py": fixture_test_template(
                    channel
                ),
            }
        )
    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    return list(files)
