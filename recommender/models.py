from sqlalchemy import ARRAY, Column, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB

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
    release_year = Column(Integer)
    price_range = Column(String)
    key_features = Column(ARRAY(String))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    raw_data = Column(JSONB)


class TaskStatus(Base):
    __tablename__ = "task_status"

    request_id = Column(String, primary_key=True)
    search_query = Column(String, index=True)
    status = Column(String)  # "processing", "complete", "error"
    progress = Column(Integer)
    error = Column(String, nullable=True)
    data = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
