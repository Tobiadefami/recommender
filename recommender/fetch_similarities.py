from typing import List

from recommender.product_categories import PRODUCT_TIERS


def fetch_similar_products(product_name: str) -> List[str]:
    product_name_lower = product_name.lower()

    product_map = {name.lower(): name for name in PRODUCT_TIERS.keys()}

    original_product_name = product_map.get(product_name_lower)

    if not original_product_name:
        return []
    product_info = PRODUCT_TIERS[original_product_name]
    category = product_info["category"]
    tier = product_info["tier"]
    release_year = product_info["release_year"]

    similar_products = [
        product
        for product, info in PRODUCT_TIERS.items()
        if info["category"] == category
        and info["tier"] == tier
        and info["release_year"] == release_year
        and product.lower() != product_name_lower
    ]
    return similar_products
