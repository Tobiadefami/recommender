import json
from pathlib import Path

from recommender.database import get_db, init_db
from recommender.models import Product, ProductFeature, ProductType


def migrate_catalogue_to_db():
    catalogue_file = Path("__file__").parent / "product_categories.json"
    with open(catalogue_file) as f:
        catalogue_data = json.load(f)

    db = next(get_db())
    try:
        # iterate through product types
        for type_name, type_data in catalogue_data.items():
            product_type = ProductType(name=type_name)
            db.add(product_type)
            db.flush() # flush to get the id of the product type

            # Add products
            for product_name, product_data in type_data["products"].items():
                product=Product(
                    name = product_name,
                    brand = product_data["brand"],
                    category = product_data["category"],
                    release_year = product_data["release_year"],
                    price_range = product_data["price_range"],
                    product_type_id = product_type.id
                )
                db.add(product)
                db.flush() # flush to get the id of the product

                # Add key features
                for product in product_data["key_features"]:
                    product_feature = ProductFeature(feature=feature, product_id=product.id)
                    db.add(product_feature)
        db.commit()
        print("Successfully migrated catalogue to database")
    except Exception as e:
        db.rollback()
        print(f"Failed to migrate catalogue to database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    migrate_catalogue_to_db()
