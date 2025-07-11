import pytest
from scraper import parse_ingredients, ingredient_grouping


def test_parse_ingredients():
    html = '<p>Ingredients: water, oil, salt.</p>'
    assert parse_ingredients(html) == ['water', 'oil', 'salt']


def test_ingredient_grouping():
    products = [
        {"ingredients": ['a', 'b', 'c']},
        {"ingredients": ['b', 'c', 'd']},
        {"ingredients": ['x', 'y']},
    ]
    grouped = ingredient_grouping(products)
    groups = [p['ingredient_group'] for p in grouped]
    assert groups[0] == groups[1]
    assert groups[2] != groups[0]
from scraper import scrape_products


def test_scrape_products():
    prods = scrape_products()
    assert len(prods) >= 10
    for p in prods:
        for key in ['product_id', 'product_line_name', 'brand_name', 'product_name',
                    'product_image_url', 'barcode', 'ingredients', 'price', 'website_name']:
            assert key in p
