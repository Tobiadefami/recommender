import logging
from typing import Dict, List, Optional

from sqlalchemy import select

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

    async def get_similar_product(self, product_name: str) -> List[Dict]:
        """
        Get similar products based on name.

        Args:
            product_name: Name of the product to find similar products for

        Returns:
            List of similar products with their details
        """
        if not self.catalogue:
            await self.initialize()

        similar_products = []
        product_name = product_name.lower()

        for name, details in self.catalogue.items():
            # Simple similarity check - can be enhanced with more sophisticated matching
            if product_name in name or name in product_name:
                similar_products.append({"name": name, **details})

        # Sort by verification status and confidence score
        similar_products.sort(
            key=lambda x: (
                x.get("verified", False),
                x.get("confidence_score", "low"),
            ),
            reverse=True,
        )

        return similar_products[:5]  # Return top 5 similar products

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
        category_products = []

        for name, details in self.catalogue.items():
            if details.get("category", "").lower() == category:
                category_products.append({"name": name, **details})

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
        brand_products = []

        for name, details in self.catalogue.items():
            if details.get("brand", "").lower() == brand:
                brand_products.append({"name": name, **details})

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

        categories = set()
        for details in self.catalogue.values():
            if category := details.get("category"):
                categories.add(category)

        return sorted(list(categories))

    def get_brands(self) -> List[str]:
        """Get list of unique brands"""
        if not self.catalogue:
            return []

        brands = set()
        for details in self.catalogue.values():
            if brand := details.get("brand"):
                brands.add(brand)

        return sorted(list(brands))
