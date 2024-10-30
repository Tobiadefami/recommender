import json
from pathlib import Path
from typing import Dict, List, Optional


class ProductCatalogue:
    def __init__(self):
        self.catalogue = self._load_catalogue()

    def _load_catalogue(self) -> Dict:
        catalogue_file = Path(__file__).parent / "product_categories.json"
        with open(catalogue_file, "r") as f:
            return json.load(f)

    def get_product_type(self, product_name: str) -> Optional[str]:
        catalogue = self.catalogue
        for product_type, data in catalogue.items():
            if product_name in data["products"]:
                return product_type
        return None

    def get_similar_product(self, product_name: str) -> Dict[str, List[str]]:
        product_type = self.get_product_type(product_name)
        if not product_type:
            return {"same_brand": [], "competitors": [], "similar_category": []}

        product_data = self.catalogue[product_type]["products"].get(
            product_name
        )
        if not product_data:
            return {"same_brand": [], "competitors": [], "similar_category": []}

        # get direct alternatives if specified
        if "alternatives" in product_data:
            return product_data["alternatives"]

        # otherwise, find similar products based on attributes
        similar_products = {
            "same_brand": [],
            "competitors": [],
            "similar_category": [],
        }

        for product, data in self.catalogue[product_type]["products"].items():
            if product == product_name:
                continue
            # same brand products in similar price range
            if (
                data["brand"] == product_data["brand"]
                and data["price_range"] == product_data["price_range"]
            ):
                similar_products["same_brand"].append(product)

            # competitors in the same category
            elif (
                data["category"] == product_data["category"]
                and data["brand"] not in product_data["brand"]
            ):
                similar_products["competitors"].append(product)

            # products in the same category
            elif data["category"] == product_data["category"]:
                similar_products["similar_category"].append(product)
        return similar_products
