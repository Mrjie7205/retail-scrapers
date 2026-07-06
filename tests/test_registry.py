import pytest

from retail_scrapers.errors import ConfigurationError
from retail_scrapers.registry import get_adapter, list_channels


def test_builtin_channels_are_registered():
    ids = {row["id"] for row in list_channels()}
    assert ids == {"amazon-de", "boulanger-fr", "currys-gb", "elkjop-no"}


def test_registry_is_case_insensitive():
    assert get_adapter("ELKJOP-NO").channel_id == "elkjop-no"


def test_unknown_channel_has_helpful_error():
    with pytest.raises(ConfigurationError, match="可用渠道"):
        get_adapter("not-a-channel")
