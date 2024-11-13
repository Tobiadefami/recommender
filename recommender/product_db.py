import json
import logging
from datetime import datetime
from typing import Dict, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from recommender.database import get_db
from recommender.models import ProductModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def save_product_info(
    product_data: str, raw_data: Optional[str] = None
) -> Optional[ProductModel]:
    """
    Save product information to the database.
    Args:
        product_data: JSON string containing product information
        raw_data: Optional raw search results/conversation
    """
    db: Session = next(get_db())

    try:
        # Parse the JSON string
        data = json.loads(product_data)

        # Extract product name and info
        product_name, info = next(iter(data.items()))

        # Check if product already exists
        existing_product = (
            db.query(ProductModel)
            .filter(
                func.lower(ProductModel.product_name)
                == func.lower(product_name)
            )
            .first()
        )

        if existing_product:
            # Update existing product
            existing_product.brand = info["brand"]
            existing_product.category = info["category"]
            existing_product.release_year = info["release_year"]
            existing_product.tier = info["tier"]
            existing_product.price_range = info["price_range"]
            existing_product.key_features = info["key_features"]
            existing_product.updated_at = datetime.utcnow()
            existing_product.raw_data = (
                raw_data if raw_data else existing_product.raw_data
            )
            product = existing_product
        else:
            # Create new product
            product = ProductModel(
                product_name=product_name,
                brand=info["brand"],
                category=info["category"],
                tier=info["tier"],
                release_year=info["release_year"],
                price_range=info["price_range"],
                key_features=info["key_features"],
                raw_data=raw_data,
            )
            db.add(product)

        db.commit()
        logger.info(f"Successfully saved/updated product: {product_name}")
        return product

    except Exception as e:
        db.rollback()
        logger.error(f"Error saving product info: {e}", exc_info=True)
        return None
    finally:
        db.close()


def get_product_from_db(product_name: str) -> Optional[Dict]:
    """Retrieve product information from the database."""
    db: Session = next(get_db())
    try:
        product = (
            db.query(ProductModel)
            .filter(
                func.lower(ProductModel.product_name)
                == func.lower(product_name)
            )
            .first()
        )
        if product:
            return {
                product.product_name: {
                    "brand": product.brand,
                    "category": product.category,
                    "tier": product.tier,
                    "release_year": product.release_year,
                    "price_range": product.price_range,
                    "key_features": product.key_features,
                }
            }
        return None
    finally:
        db.close()
