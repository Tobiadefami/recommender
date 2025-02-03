import json
import logging
from datetime import datetime
from typing import Dict, Optional

from sqlalchemy import func, select

from recommender.database import get_db
from recommender.models import ProductModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_product_data(info: Dict) -> Dict:
    """Validate and clean product information"""
    cleaned_data = {}

    # Handle release year
    release_year = info.get("release_year")
    if isinstance(release_year, int):
        cleaned_data["release_year"] = str(release_year)
    else:
        cleaned_data["release_year"] = "unverified"

    # Handle required string fields
    string_fields = ["brand", "category", "tier", "price_range", "release_year"]
    for field in string_fields:
        value = info.get(field)
        cleaned_data[field] = value if isinstance(value, str) else "unverified"

    # Handle key features
    key_features = info.get("key_features", [])
    cleaned_data["key_features"] = (
        [str(f) for f in key_features] if key_features else []
    )

    # Handle confidence score
    cleaned_data["confidence_score"] = info.get("confidence_score", "low")

    # Handle verification
    cleaned_data["verified"] = all(
        cleaned_data[field] != "unverified" for field in string_fields
    )

    # Handle sources
    cleaned_data["sources"] = info.get("sources", [])

    return cleaned_data


async def save_product_info(
    product_data: str, raw_data: Optional[str] = None
) -> Optional[ProductModel]:
    """
    Save product information to the database.
    Args:
        product_data: JSON string containing product information
        raw_data: Optional raw search results/conversation
    """
    async for db in get_db():
        try:
            # Parse the JSON string
            data = json.loads(product_data)

            # Extract product name and info
            product_name, info = next(iter(data.items()))

            # Validate and clean product information
            cleaned_info = validate_product_data(info)

            # Check if product already exists
            result = await db.execute(
                select(ProductModel).filter(
                    func.lower(ProductModel.product_name)
                    == func.lower(product_name)
                )
            )
            existing_product = result.scalar_one_or_none()

            if existing_product:
                # Update existing product
                for key, value in cleaned_info.items():
                    setattr(existing_product, key, value)

                existing_product.updated_at = datetime.utcnow()
                existing_product.verification_date = datetime.utcnow()
                existing_product.raw_data = (
                    raw_data if raw_data else existing_product.raw_data
                )
                product = existing_product
            else:
                # Create new product
                product = ProductModel(
                    product_name=product_name,
                    brand=cleaned_info["brand"],
                    category=cleaned_info["category"],
                    tier=cleaned_info["tier"],
                    release_year=cleaned_info["release_year"],
                    price_range=cleaned_info["price_range"],
                    key_features=cleaned_info["key_features"],
                    confidence_score=cleaned_info["confidence_score"],
                    verified=cleaned_info["verified"],
                    verification_date=datetime.utcnow(),
                    source_url=cleaned_info["sources"],
                    raw_data=raw_data,
                )
                db.add(product)

            await db.commit()
            logger.info(f"Successfully saved/updated product: {product_name}")
            return product

        except Exception as e:
            await db.rollback()
            logger.error(f"Error saving product info: {e}", exc_info=True)
            return None


async def get_product_from_db(product_name: str) -> Optional[Dict]:
    """Retrieve product information from the database."""
    async for db in get_db():
        try:
            result = await db.execute(
                select(ProductModel).filter(
                    func.lower(ProductModel.product_name)
                    == func.lower(product_name)
                )
            )
            product = result.scalar_one_or_none()

            if product:
                return {
                    product.product_name: {
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
                }
            return None

        except Exception as e:
            logger.error(f"Error retrieving product: {e}", exc_info=True)
            return None
