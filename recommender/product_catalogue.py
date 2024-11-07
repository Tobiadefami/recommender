from typing import Dict, List, Optional

from recommender.database import get_db
from recommender.models import Product, ProductType


class ProductCatalogue:
    def __init__(self):
        self.catalogue = self._load_catalogue()
        self.normalized_product_map = self._build_normalized_product_name_map()

    def _load_catalogue(self) -> Dict:
        db = next(get_db())
        try:
            catalogue = {}
            product_types = db.query(ProductType).all()
            for product_type in product_types:
                catalogue[product_type.name] = {
                    "products": [],
                }
                for product in product_type.products:
                    catalogue[product.name]["products"][product.name] = {
                        "brand": product.brand,
                        "category": product.category,
                        "release_year": product.release_year,
                        "price_range": product.price_range,
                        "key_features": [
                            feature.feature for feature in product.key_features
                        ],
                    }
            return catalogue
        finally:
            db.close()

    def _build_normalized_product_name_map(self) -> Dict[str, str]:
        """logic to build a map of normalised product names"""
        db = next(get_db())
        try:
            products = db.query(Product).all()
            return {product.name.lower(): product.name for product in products}
        finally:
            db.close()

    def _normalize_product_name(self, product_name: str) -> Optional[str]:
        """convert to lowercase"""
        return self.normalized_product_map.get(product_name.lower())

    def get_product_type(self, product_name: str) -> Optional[str]:
        normalized_product_name = self._normalize_product_name(product_name)
        if not normalized_product_name:
            return None

        catalogue = self.catalogue

        for product_type, data in catalogue.items():
            if normalized_product_name in data["products"]:
                return product_type
        return None

    def get_similar_product(self, product_name: str) -> Dict[str, List[str]]:
        normalized_product_name = self._normalize_product_name(product_name)
        if not normalized_product_name:
            return {"same_brand": [], "competitors": [], "similar_category": []}
        product_type = self.get_product_type(normalized_product_name)
        if not product_type:
            return {"same_brand": [], "competitors": [], "similar_category": []}

        product_data = self.catalogue[product_type]["products"].get(
            normalized_product_name
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
            if product == normalized_product_name:
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
