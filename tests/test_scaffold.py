from pathlib import Path

import pytest

from retail_scrapers.scaffold import (
    class_name,
    create_adapter_scaffold,
    package_name,
)


def test_channel_id_to_package_and_class_name():
    assert package_name("example-shop-us") == "example_shop_us"
    assert class_name("example-shop-us") == "ExampleShopUsAdapter"


def test_rejects_invalid_channel_id():
    with pytest.raises(ValueError, match="channel_id"):
        package_name("Example Shop")


def test_create_adapter_scaffold(tmp_path: Path):
    created = create_adapter_scaffold(
        "example-shop-us",
        display_name="Example Shop US",
        country="US",
        root=tmp_path,
    )

    assert [path.relative_to(tmp_path).as_posix() for path in created] == [
        "src/retail_scrapers/adapters/example_shop_us/__init__.py",
        "src/retail_scrapers/adapters/example_shop_us/adapter.py",
        "tests/test_example_shop_us_adapter.py",
    ]
    adapter = (tmp_path / "src/retail_scrapers/adapters/example_shop_us/adapter.py").read_text(
        encoding="utf-8"
    )
    assert 'channel_id = "example-shop-us"' in adapter
    assert 'display_name = "Example Shop US"' in adapter
    assert 'country = "US"' in adapter


def test_create_adapter_scaffold_refuses_overwrite(tmp_path: Path):
    create_adapter_scaffold("example-shop-us", root=tmp_path)

    with pytest.raises(FileExistsError, match="already exists"):
        create_adapter_scaffold("example-shop-us", root=tmp_path)


def test_create_adapter_scaffold_with_fixtures(tmp_path: Path):
    created = create_adapter_scaffold("example-shop-us", root=tmp_path, with_fixtures=True)
    relative = {path.relative_to(tmp_path).as_posix() for path in created}

    assert "tests/fixtures/example_shop_us/catalog.sample.json" in relative
    assert "tests/fixtures/example_shop_us/price.sample.json" in relative
    assert "tests/test_example_shop_us_fixtures.py" in relative

    fixture = (tmp_path / "tests/fixtures/example_shop_us/catalog.sample.json").read_text(
        encoding="utf-8"
    )
    assert '"channel": "example-shop-us"' in fixture
    assert "example.com" in fixture
