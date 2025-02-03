from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from recommender.environment_vars import DATABASE_URL

# Make sure DATABASE_URL uses postgresql+asyncpg:// instead of postgresql://
engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

Base = declarative_base()


def register_models():
    """Import all models to register them with SQLAlchemy"""
    from recommender.models import (  # noqa: F401
        Posts,
        ProductModel,
        Review,
        SearchHistory,
        StructuredOutput,
        User,
    )
    # The imports themselves register the models


async def init_db():
    register_models()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
