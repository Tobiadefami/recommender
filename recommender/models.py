from sqlalchemy import Column, Integer, String,  DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class RedditPost(Base):
    __tablename__ = 'reddit_posts'

    id = Column(String, primary_key=True)
    search_query=Column(String, index=True)
    created_at = Column(DateTime, index=True)
    data = Column(JSONB)
