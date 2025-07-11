import requests
from bs4 import BeautifulSoup
import re
import csv
from collections import defaultdict

SHOP_URL = "https://gtworld.de"


def fetch_products(limit=250):
    url = f"{SHOP_URL}/products.json?limit={limit}"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json().get("products", [])


def parse_ingredients(html):
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator="\n")
    # Look for patterns Ingredients: or Zutaten:
    match = re.search(r"(?:Ingredients|Zutaten|Inhaltsstoffe)\s*[:\-]\s*(.*)", text, re.IGNORECASE)
    if match:
        ingredients_part = match.group(1)
        # stop at newline or period
        ingredients_part = ingredients_part.split("\n")[0]
        ingredients_part = ingredients_part.split(".")[0]
        # split by comma
        return [ing.strip() for ing in re.split(r",|;", ingredients_part) if ing.strip()]
    return []


def scrape_products(min_count=10):
    products = fetch_products()
    result = []
    for p in products:
        if len(result) >= min_count:
            break
        variant = p.get("variants", [{}])[0]
        data = {
            "product_id": variant.get("sku") or str(p.get("id")),
            "product_line_name": p.get("product_type"),
            "brand_name": p.get("vendor"),
            "product_name": p.get("title"),
            "product_image_url": p.get("image", {}).get("src") or (p.get("images") or [{}])[0].get("src"),
            "barcode": variant.get("barcode"),
            "ingredients": parse_ingredients(p.get("body_html")),
            "price": variant.get("price"),
            "website_name": SHOP_URL,
        }
        result.append(data)
    return result


def ingredient_grouping(products):
    groups = []
    group_ids = {}
    for i, prod in enumerate(products):
        ing_set = set(ing.lower() for ing in prod.get("ingredients", []))
        assigned = False
        for gid, gset in groups:
            if len(ing_set & gset) >= 2:
                group_ids[i] = gid
                gset.update(ing_set)
                assigned = True
                break
        if not assigned:
            gid = len(groups) + 1
            groups.append((gid, set(ing_set)))
            group_ids[i] = gid
    for idx, prod in enumerate(products):
        prod["ingredient_group"] = group_ids.get(idx)
    return products


def save_to_csv(products, filename="products.csv"):
    if not products:
        return
    fieldnames = list(products[0].keys())
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for prod in products:
            writer.writerow(prod)


if __name__ == "__main__":
    scraped = scrape_products()
    grouped = ingredient_grouping(scraped)
    save_to_csv(grouped)
    print(f"Saved {len(grouped)} products to products.csv")
