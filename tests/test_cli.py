import json

import pytest

from retail_scrapers.cli import main


def test_channels_command(capsys):
    assert main(["channels"]) == 0
    rows = json.loads(capsys.readouterr().out)
    assert {row["id"] for row in rows} == {
        "amazon-de",
        "boulanger-fr",
        "currys-gb",
        "elkjop-no",
    }


def test_health_command(capsys):
    assert main(["health"]) == 0
    rows = json.loads(capsys.readouterr().out)
    assert {row["channel"] for row in rows} == {
        "amazon-de",
        "boulanger-fr",
        "currys-gb",
        "elkjop-no",
    }


def test_health_markdown_command(capsys):
    assert main(["health", "--format", "markdown"]) == 0
    output = capsys.readouterr().out
    assert "| Channel | Market |" in output
    assert "`elkjop-no`" in output


def test_schema_command(capsys):
    assert main(["schema", "catalog"]) == 0
    rows = json.loads(capsys.readouterr().out)
    assert rows["record"] == "CatalogRecord"
    assert "sku" in rows["properties"]


def test_schema_markdown_command(capsys):
    assert main(["schema", "price", "--format", "markdown"]) == 0
    output = capsys.readouterr().out
    assert "## PriceRecord" in output
    assert "`status`" in output


def test_scaffold_command_prints_next_steps(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)

    assert main(["scaffold", "example-shop-us", "--with-fixtures"]) == 0
    output = json.loads(capsys.readouterr().out)

    assert output["created"]
    assert output["created"][0] == "src/retail_scrapers/adapters/example_shop_us/__init__.py"
    assert output["instructions"]["adapter_class"] == "ExampleShopUsAdapter"
    assert "registry.py" in " ".join(output["instructions"]["next_steps"])


def test_runtime_options_are_validated(capsys):
    assert main(["catalog", "--channel", "elkjop-no", "--timeout-ms", "0"]) == 1
    assert "timeout_ms" in capsys.readouterr().err


def test_unknown_cli_argument_still_fails_fast():
    with pytest.raises(SystemExit):
        main(["catalog", "--channel", "elkjop-no", "--not-a-real-option"])
