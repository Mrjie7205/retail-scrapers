from retail_scrapers.adapters.boulanger_fr.adapter import BoulangerFrAdapter


def test_boulanger_html_parser_keeps_product_price_inside_its_card():
    html = """
    <ul>
      <li class="product-list__item">
        <article>
          <a href="/ref/1234567">TV Example X100 55"</a>
        </article>
        <p class="price__amount">999,00€</p>
      </li>
      <li class="product-list__item">
        <article>
          <a href="/ref/7654321">TV Example Y200 65"</a>
        </article>
        <p class="price__amount">1 499,00€</p>
      </li>
    </ul>
    """
    rows = BoulangerFrAdapter._rows_from_html(html)
    by_href = {row["href"]: row for row in rows}
    assert by_href["/ref/1234567"]["price"] == "999,00€"
    assert by_href["/ref/7654321"]["price"] == "1 499,00€"
