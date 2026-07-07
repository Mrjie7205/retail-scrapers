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


def test_runtime_options_are_validated(capsys):
    assert main(["catalog", "--channel", "elkjop-no", "--timeout-ms", "0"]) == 1
    assert "timeout_ms" in capsys.readouterr().err


def test_unknown_cli_argument_still_fails_fast():
    with pytest.raises(SystemExit):
        main(["catalog", "--channel", "elkjop-no", "--not-a-real-option"])
