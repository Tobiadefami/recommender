from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import expression

from recommender.models import Review, SearchHistory, StructuredOutput


async def get_user_search_analytics(
    user_id: int, db: AsyncSession, limit: Optional[int] = None
):
    """Get analytics for a user's searches with review metrics"""
    query = (
        select(
            SearchHistory.search_query,
            SearchHistory.searched_at,
            func.count(Review.id).label("result_count"),
            func.avg(Review.star_rating).label("average_rating"),
            # Use coalesce to handle null cases
            func.coalesce(
                func.mode().within_group(expression.asc(Review.sentiment)),
                "neutral",
            ).label("overall_sentiment"),
        )
        .outerjoin(SearchHistory.structured_output)
        .outerjoin(StructuredOutput.reviews)
        .filter(SearchHistory.user_id == user_id)
        .group_by(
            SearchHistory.id,
            SearchHistory.search_query,
            SearchHistory.searched_at,
        )
        .order_by(SearchHistory.searched_at.desc())
    )

    if limit:
        query = query.limit(limit)

    result = await db.execute(query)
    return result.all()


def format_analytics_result(analytics):
    """Format analytics results for API response"""
    return [
        {
            "query": item.search_query,
            "timestamp": item.searched_at,
            "resultCount": item.result_count or 0,
            "averageRating": float(item.average_rating)
            if item.average_rating
            else 0.0,
            "sentiment": item.overall_sentiment or "neutral",
        }
        for item in analytics
    ]
