"""内置渠道注册表。"""

from __future__ import annotations

from .adapters.amazon_de import AmazonDeAdapter
from .adapters.boulanger_fr import BoulangerFrAdapter
from .adapters.currys_gb import CurrysGbAdapter
from .adapters.elkjop_no import ElkjopNoAdapter
from .errors import ConfigurationError

ADAPTERS = {
    adapter.channel_id: adapter
    for adapter in (
        AmazonDeAdapter(),
        BoulangerFrAdapter(),
        CurrysGbAdapter(),
        ElkjopNoAdapter(),
    )
}


def get_adapter(channel: str):
    key = (channel or "").strip().lower()
    try:
        return ADAPTERS[key]
    except KeyError as exc:
        raise ConfigurationError(
            f"不支持的渠道 {channel!r}；可用渠道: {', '.join(sorted(ADAPTERS))}"
        ) from exc


def list_channels() -> list[dict[str, str | bool]]:
    return [ADAPTERS[key].info() for key in sorted(ADAPTERS)]
