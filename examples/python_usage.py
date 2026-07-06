from retail_scrapers import scrape_catalog

records = scrape_catalog(
    "elkjop-no",
    years=[2025, 2026],
    max_items=5,
)

for record in records:
    print(record.to_dict())
