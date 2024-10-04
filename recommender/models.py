from sqlalchemy import Column, DateTime, Integer, String
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
