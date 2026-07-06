from retail_scrapers.adapters.currys_gb.adapter import _brand, _size, _slug_title


def test_currys_slug_is_stable_product_text():
    slug = "example-x100-55-oled-4k-smart-tv-123456"
    assert _brand(slug) == "Example"
    assert _size(slug, "") == 55.0
    assert _slug_title(slug) == "example x100 55 oled 4k smart tv"
