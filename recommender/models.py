from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from recommender.database import Base


class Posts(Base):
    __tablename__ = "posts"

    id = Column(String, primary_key=True)
    source = Column(String, index=True)
    search_query = Column(String, index=True)
    created_at = Column(DateTime, index=True)
    raw_data = Column(JSONB)


class StructuredOutput(Base):
    __tablename__ = "structured_outputs"
    id = Column(Integer, primary_key=True)
    search_query = Column(String, index=True)
    data = Column(JSONB)


class ProductType(Base):
    __tablename__ = "product_types"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    products = relationship("Product", back_populates="product_type")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    brand = Column(String)
    category = Column(String)
    release_year = Column(Integer)
    price_range = Column(String)
    product_type_id = Column(Integer, ForeignKey("product_types.id"))
    product_type = relationship("ProductType", back_populates="products")
    key_features = relationship("ProductFeature", back_populates="product")


class ProductFeature(Base):
    __tablename__ = "product_features"

    id = Column(Integer, primary_key=True)
    feature = Column(String)
    product_id = Column(Integer, ForeignKey("products.id"))
    product = relationship("Product", back_populates="key_features")
