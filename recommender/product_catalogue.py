import json
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from recommender.database import get_db
from recommender.models import ProductModel
from recommender.product_agent import get_product_information


class ProductCatalogue:
    def __init__(self):
        self.catalogue = self._load_catalogue()
        self.normalized_product_map = self._build_normalized_product_name_map()

    def _load_catalogue(self) -> Dict:
        """Load products from database"""
        catalogue = {}
        # load from database
        db: Session = next(get_db())
        try:
            db_products = db.query(ProductModel).all()
            for product in db_products:
                catalogue[product.product_name] = {
                    "brand": product.brand,
                    "category": product.category,
                    "release_year": product.release_year,
                    "tier": product.tier,
                    "price_range": product.price_range,
                    "key_features": product.key_features,
                }
        except Exception as e:
            print(f"Error loading product catalogue: {e}")
        finally:
            db.close()
        return catalogue

    def _build_normalized_product_name_map(self) -> Dict[str, str]:
        """logic to build a map of normalised product names"""
        return {
            product_name.lower(): product_name
            for product_name in self.catalogue.keys()
        }

    def _normalize_product_name(self, product_name: str) -> Optional[str]:
        """convert to lowercase"""
        return self.normalized_product_map.get(product_name.lower())

    def get_product_info(self, product_name: str) -> Optional[Dict]:
        normalized_product_name = self._normalize_product_name(product_name)

        if (
            normalized_product_name
            and normalized_product_name in self.catalogue
        ):
            print(f"using cached product info for {product_name}")
            return {
                normalized_product_name: self.catalogue[normalized_product_name]
            }

        # if not found, fetch new information
        try:
            new_info = get_product_information(product_name)
            if new_info:
                # parse the json string if it is a string
                if isinstance(new_info, str):
                    new_info = json.loads(new_info)
                # refresh catalogue
                self.catalogue = self._load_catalogue()
                self.normalized_product_map = (
                    self._build_normalized_product_name_map()
                )
                return new_info
        except Exception as e:
            print(f"Error fetching product info: {e}")
        return None

    def get_similar_product(self, product_name: str) -> Dict[str, List[str]]:
        """Find similar products based on brand, category, and key features"""
        product_info = self.get_product_info(product_name)
        if not product_info:
            return {"same_brand": [], "same_category": [], "same_features": []}

        # Extract product info
        searched_product_name, product_data = next(iter(product_info.items()))
        target_brand = product_data["brand"]
        target_category = product_data["category"]
        target_tier = product_data["tier"]

        similar_products = {
            "same_brand": [],
            "similar_category": [],
            "competitors": [],
        }

        for name, info in self.catalogue.items():
            if name.lower() == searched_product_name.lower():
                continue
            if (
                info["brand"] == target_brand
                and info["category"] == target_category
            ):
                similar_products["same_brand"].append(name)

            elif (
                info["category"] == target_category
                and info["brand"] != target_brand
            ):
                similar_products["similar_category"].append(name)
            elif (
                info["category"] == target_category
                and info["tier"] == target_tier
                and info["brand"] != target_brand
            ):
                similar_products["competitors"].append(name)
        return similar_products
