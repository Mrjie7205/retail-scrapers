from retail_scrapers.health import list_channel_health


def test_channel_health_covers_builtin_adapters():
    rows = list_channel_health()
    assert {row["channel"] for row in rows} == {
        "amazon-de",
        "boulanger-fr",
        "currys-gb",
        "elkjop-no",
    }
    assert all(row["catalog_strategy"] for row in rows)
    assert all(row["price_strategy"] for row in rows)
    assert all(row["maintenance_risk"] for row in rows)
