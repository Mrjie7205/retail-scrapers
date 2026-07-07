"""Channel health metadata for docs and CLI output."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class ChannelHealth:
    channel: str
    market: str
    catalog_strategy: str
    price_strategy: str
    validation: str
    maintenance_risk: str
    live_smoke: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


CHANNEL_HEALTH = (
    ChannelHealth(
        channel="amazon-de",
        market="Germany",
        catalog_strategy="Playwright search pages with delivery-location session",
        price_strategy="Product page schema/selector parsing with native EUR validation",
        validation="Filters obvious non-TV results; validates EUR prices",
        maintenance_risk="High: search-page layout and anti-automation behavior may drift",
        live_smoke="Run Manual live smoke test with channel=amazon-de",
    ),
    ChannelHealth(
        channel="boulanger-fr",
        market="France",
        catalog_strategy="Server HTML parsing with brand facets",
        price_strategy="HTML Schema.org first, Playwright page fallback",
        validation="Card-level price parsing; native EUR price checks",
        maintenance_risk="Medium: product card markup may change",
        live_smoke="Run Manual live smoke test with channel=boulanger-fr",
    ),
    ChannelHealth(
        channel="currys-gb",
        market="United Kingdom",
        catalog_strategy="Isolated Playwright sessions for paginated category pages",
        price_strategy="Product page Schema.org first, selector fallback",
        validation="Total-count validation when running an unfiltered full catalog",
        maintenance_risk="High: category pages can be sensitive to session and layout changes",
        live_smoke="Run Manual live smoke test with channel=currys-gb",
    ),
    ChannelHealth(
        channel="elkjop-no",
        market="Norway",
        catalog_strategy="Algolia catalog API with signed public frontend key",
        price_strategy="tRPC dynamic product data API, page fallback",
        validation="Total/page/SKU/year checks for strict catalog extraction",
        maintenance_risk="Medium: frontend API contracts or signed-key endpoint may change",
        live_smoke="Run Manual live smoke test with channel=elkjop-no",
    ),
)


def list_channel_health() -> list[dict[str, str]]:
    return [row.to_dict() for row in CHANNEL_HEALTH]


def channel_health_markdown() -> str:
    headers = [
        "Channel",
        "Market",
        "Catalog strategy",
        "Price strategy",
        "Validation",
        "Maintenance risk",
    ]
    lines = [
        "| " + " | ".join(headers) + " |",
        "|---|---|---|---|---|---|",
    ]
    for row in CHANNEL_HEALTH:
        values = [
            f"`{row.channel}`",
            row.market,
            row.catalog_strategy,
            row.price_strategy,
            row.validation,
            row.maintenance_risk,
        ]
        lines.append("| " + " | ".join(_escape_markdown_cell(value) for value in values) + " |")
    return "\n".join(lines)


def _escape_markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")
