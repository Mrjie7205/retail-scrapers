import pytest

from retail_scrapers.errors import CompletenessError
from retail_scrapers.models import CatalogRecord, PriceRecord
from retail_scrapers.validation import validate_catalog, validate_price_run


def _catalog(sku: str) -> CatalogRecord:
    return CatalogRecord(
        channel="example-channel",
        country="XX",
        sku=sku,
        brand="Example",
        title=f"Example product {sku}",
        url=f"https://example.com/{sku}",
    )


def test_catalog_accepts_unique_complete_rows():
    rows = [_catalog("1"), _catalog("2")]
    assert validate_catalog(rows, expected_count=2) == rows


def test_catalog_rejects_duplicate_sku():
    with pytest.raises(CompletenessError, match="重复"):
        validate_catalog([_catalog("1"), _catalog("1")])


def test_catalog_rejects_wrong_expected_count():
    with pytest.raises(CompletenessError, match="不一致"):
        validate_catalog([_catalog("1")], expected_count=2)


def test_price_run_applies_success_threshold():
    rows = [
        PriceRecord("example", "XX", "1", "https://example.com/1", 10, "EUR", "success"),
        PriceRecord("example", "XX", "2", "https://example.com/2", None, "", "failed"),
    ]
    assert validate_price_run(rows, minimum_success_rate=0.5) == rows
    with pytest.raises(CompletenessError, match="成功率"):
        validate_price_run(rows, minimum_success_rate=0.8)
