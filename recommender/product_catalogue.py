import logging
from typing import Dict, List, Optional

from sqlalchemy import select

from recommender.agent import Agent
from recommender.database import get_db
from recommender.models import ProductModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductCatalogue:
    def __init__(self):
        self.catalogue: Optional[Dict] = None

    async def initialize(self):
        """Initialize the catalogue asynchronously"""
        self.catalogue = await self._load_catalogue()
        return self

    async def _load_catalogue(self) -> Dict:
        """Load product catalogue from database"""
        catalogue = {}
        async for db in get_db():
            try:
                result = await db.execute(
                    select(ProductModel).order_by(ProductModel.product_name)
                )
                products = result.scalars().all()

                for product in products:
                    print("WE ARE IN THE PRODUCTS DATABASE")
                    catalogue[product.product_name.lower()] = {
                        "brand": product.brand,
                        "category": product.category,
                        "tier": product.tier,
                        "release_year": product.release_year,
                        "price_range": product.price_range,
                        "key_features": product.key_features,
                        "confidence_score": product.confidence_score,
                        "verified": product.verified,
                        "verification_date": product.verification_date.isoformat()
                        if product.verification_date
                        else None,
                        "source_url": product.source_url,
                    }
                return catalogue
            except Exception as e:
                logger.error(f"Error loading catalogue: {e}")
                return {}

    async def get_similar_product(self, product_name: str) -> Dict:
        """
        Main method for product comparison feature.
        Returns categorized similar products matching the frontend interface.
        """
        if not self.catalogue:
            await self.initialize()

        agent = Agent()
        search_product_info = await agent.get_information(product_name)
        logger.info(f"SEARCH PRODUCT INFORMATION >>> {search_product_info}")
        if not search_product_info:
            return {"same_brand": [], "competitors": [], "similar_category": []}

        # Extract standardized information
        search_product_name = next(iter(search_product_info))
        search_details = search_product_info[search_product_name]

        # Extract standardized information
        search_brand = search_details["brand"].lower()
        search_category = search_details["category"].lower()
        search_tier = search_details["tier"].lower()

        same_brand = []
        competitors = []
        similar_category = []

        # Categorize products using standardized fields
        for db_product_name, db_product_details in self.catalogue.items():
            if db_product_name.lower() == product_name.lower():
                continue

            db_brand = db_product_details["brand"].lower()
            db_category = db_product_details["category"].lower()
            db_tier = db_product_details["tier"].lower()

            # Same brand products
            if db_brand == search_brand:
                same_brand.append(db_product_name)
            # Direct competitors (same category & tier, different brand)
            elif (
                db_category == search_category
                and db_tier == search_tier
                and db_brand != search_brand
            ):
                competitors.append(db_product_name)
            # Similar category products
            elif db_category == search_category:
                similar_category.append(db_product_name)

        return {
            "same_brand": same_brand[:5],
            "competitors": competitors[:5],
            "similar_category": similar_category[:5],
        }

    async def search_by_category(self, category: str) -> List[Dict]:
        """
        Search products by category.

        Args:
            category: Product category to search for

        Returns:
            List of products in the specified category
        """
        if not self.catalogue:
            await self.initialize()

        category = category.lower()

        category_products = [
            {"name": name, **details}
            for name, details in self.catalogue.items()
            if details.get("category", "").lower() == category
        ]
        # Sort by verification status and confidence score
        category_products.sort(
            key=lambda x: (
                x.get("verified", False),
                x.get("confidence_score", "low"),
            ),
            reverse=True,
        )

        return category_products

    async def search_by_brand(self, brand: str) -> List[Dict]:
        """
        Search products by brand.

        Args:
            brand: Brand name to search for

        Returns:
            List of products from the specified brand
        """
        if not self.catalogue:
            await self.initialize()

        brand = brand.lower()

        brand_products = [
            {"name": name, **details}
            for name, details in self.catalogue.items()
            if details.get("brand", "").lower() == brand
        ]
        # Sort by verification status and confidence score
        brand_products.sort(
            key=lambda x: (
                x.get("verified", False),
                x.get("confidence_score", "low"),
            ),
            reverse=True,
        )

        return brand_products

    def get_categories(self) -> List[str]:
        """Get list of unique product categories"""
        if not self.catalogue:
            return []

        return sorted(
            {
                details.get("category")
                for details in self.catalogue.values()
                if details.get("category")
            }
        )

    def get_brands(self) -> List[str]:
        """Get list of unique brands"""
        if not self.catalogue:
            return []

        return sorted(
            {
                details.get("brand")
                for details in self.catalogue.values()
                if details.get("brand")
            }
        )
