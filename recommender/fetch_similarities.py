from typing import List

from recommender.product_categories import PRODUCT_TIERS


def fetch_similar_products(product_name: str) -> List[str]:
    product_info = PRODUCT_TIERS.get(product_name, None)

    if not product_info:
        return []
    category = product_info["category"]
    tier = product_info["tier"]
    release_year = product_info["release_year"]

    similar_products = [
        product
        for product, info in PRODUCT_TIERS.items()
        if info["category"] == category
        and info["tier"] == tier
        and info["release_year"] == release_year
        and product != product_name
    ]
    return similar_products
