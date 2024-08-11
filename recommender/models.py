from sqlalchemy import create_engine, DateTime, Column, Integer, String, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./reddit_data.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class RedditSubmission(Base):
    __tablename__ = "reddit_submissions"

    id = Column(String(10), primary_key=True, index=True)
    title = Column(String(500), index=True)
    score = Column(Integer)
    url = Column(String(500))
    num_comments = Column(Integer)
    created = Column(DateTime)
    body = Column(Text)


def init_db():
    Base.metadata.create_all(bind=engine)
