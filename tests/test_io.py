import csv
import json

from retail_scrapers.input import read_targets
from retail_scrapers.models import CatalogRecord
from retail_scrapers.output import write_records


def test_read_csv_targets(tmp_path):
    path = tmp_path / "products.csv"
    path.write_text("id,url,note\none,https://example.com/1,hello\n", encoding="utf-8")
    targets = read_targets(path)
    assert targets[0].id == "one"
    assert targets[0].url == "https://example.com/1"
    assert targets[0].metadata == {"note": "hello"}


def test_write_jsonl(tmp_path):
    path = tmp_path / "out.jsonl"
    record = CatalogRecord(
        channel="example",
        country="XX",
        sku="1",
        brand="Example",
        title="Example",
        url="https://example.com/1",
    )
    write_records([record], output=path, output_format="jsonl")
    row = json.loads(path.read_text(encoding="utf-8"))
    assert row["sku"] == "1"
    assert row["metadata"] == {}


def test_write_csv_flattens_metadata(tmp_path):
    path = tmp_path / "out.csv"
    record = CatalogRecord(
        channel="example",
        country="XX",
        sku="1",
        brand="Example",
        title="Example",
        url="https://example.com/1",
        metadata={"source": "fixture"},
    )
    write_records([record], output=path, output_format="csv")
    with path.open(encoding="utf-8", newline="") as handle:
        row = next(csv.DictReader(handle))
    assert json.loads(row["metadata"]) == {"source": "fixture"}
