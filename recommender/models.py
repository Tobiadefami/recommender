from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Posts(Base):
    __tablename__ = "posts"

    id = Column(String, primary_key=True)
    source = Column(String, index=True)
    url = Column(String, index=True)
    search_query = Column(String, index=True)
    created_at = Column(DateTime, index=True)
    data = Column(JSONB)
