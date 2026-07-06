"""渠道插件协议。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from ..core.browser import BrowserRuntime
from ..models import CatalogRecord, PriceRecord, PriceTarget
from ..options import CatalogOptions, PriceOptions


class ChannelAdapter(ABC):
    channel_id: str
    display_name: str
    country: str
    supports_catalog: bool = True
    supports_prices: bool = True

    @abstractmethod
    async def scrape_catalog(
        self,
        runtime: BrowserRuntime,
        options: CatalogOptions,
    ) -> Sequence[CatalogRecord]:
        raise NotImplementedError

    @abstractmethod
    async def scrape_prices(
        self,
        runtime: BrowserRuntime,
        targets: Sequence[PriceTarget],
        options: PriceOptions,
    ) -> Sequence[PriceRecord]:
        raise NotImplementedError

    def info(self) -> dict[str, str | bool]:
        return {
            "id": self.channel_id,
            "name": self.display_name,
            "country": self.country,
            "catalog": self.supports_catalog,
            "prices": self.supports_prices,
        }
