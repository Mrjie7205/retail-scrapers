import pytest

from retail_scrapers.schema import all_schemas, record_schema, schema_markdown


def test_record_schema_exposes_catalog_contract():
    schema = record_schema("catalog")
    assert schema["record"] == "CatalogRecord"
    assert "channel" in schema["required"]
    assert schema["properties"]["price"]["type"] == "float | None"


def test_all_schemas_include_public_records():
    schemas = all_schemas()
    assert set(schemas) == {"catalog", "price", "target"}


def test_schema_markdown_contains_price_record():
    text = schema_markdown("price")
    assert "## PriceRecord" in text
    assert "`status`" in text


def test_unknown_schema_has_helpful_error():
    with pytest.raises(ValueError, match="unknown schema"):
        record_schema("missing")
