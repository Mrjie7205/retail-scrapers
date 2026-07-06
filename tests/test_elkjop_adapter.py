from retail_scrapers.adapters.elkjop_no.adapter import ElkjopNoAdapter
from retail_scrapers.options import CatalogOptions


def test_elkjop_payload_without_filters_is_general():
    payload = ElkjopNoAdapter._payload(CatalogOptions(), None, 0)
    request = payload["requests"][0]
    assert request["facetFilters"] == []
    assert request["filters"] == "productTaxonomy.id:PT351"


def test_elkjop_payload_uses_user_filters():
    options = CatalogOptions(brands=["LG", "Sony"], years=[2026])
    payload = ElkjopNoAdapter._payload(options, 2026, 2)
    request = payload["requests"][0]
    assert ["attributes.33627:2026"] in request["facetFilters"]
    assert ["brand:LG", "brand:Sony"] in request["facetFilters"]
    assert request["page"] == 2
