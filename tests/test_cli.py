import json

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
