from sqlalchemy import (
    ARRAY,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
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


class ProductModel(Base):
    __tablename__ = "product_catalogue"

    id = Column(Integer, primary_key=True)
    product_name = Column(String, unique=True, index=True)
    brand = Column(String, index=True)
    category = Column(String, index=True)
    tier = Column(String)
    release_year = Column(String)
    price_range = Column(String)
    key_features = Column(ARRAY(String))
    confidence_score = Column(String)
    verified = Column(Boolean, default=False)
    verification_date = Column(DateTime(timezone=True))
    source_url = Column(ARRAY(String))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    raw_data = Column(JSONB)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship with search history
    search_history = relationship("SearchHistory", back_populates="user")


class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    search_query = Column(String, index=True)
    searched_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship with User
    user = relationship("User", back_populates="search_history")
