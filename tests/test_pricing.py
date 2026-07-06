import pytest

from retail_scrapers.core.pricing import clean_price


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1.299,00 €", (1299.0, "EUR")),
        ("£1,249.99", (1249.99, "GBP")),
        ("24 990 kr", (24990.0, "NOK")),
        ("399,00 EUR", (399.0, "EUR")),
        ("1,299.00 USD", (1299.0, "USD")),
    ],
)
def test_clean_price_locales(text, expected):
    assert clean_price(text) == expected


def test_clean_price_rejects_empty_or_zero():
    assert clean_price("") is None
    assert clean_price("0 EUR") is None
