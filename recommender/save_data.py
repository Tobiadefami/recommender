import logging
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio.session import AsyncSession

from recommender.database import engine
from recommender.models import Base, Posts, Review, StructuredOutput

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    Base.metadata.create_all(bind=engine)


async def save_data(all_submissions: dict, db: AsyncSession):
    try:
        for search_query, submissions_list in all_submissions.items():
            result = await db.execute(
                select(func.max(Posts.created_at)).filter(
                    func.lower(Posts.search_query) == func.lower(search_query)
                )
            )
            latest_submissions = result.scalar()

            for submission_dict in submissions_list:
                await save_submissions(
                    db,
                    search_query,
                    submission_dict["reddit"],
                    "reddit",
                    latest_submissions,
                )
                await save_submissions(
                    db,
                    search_query,
                    submission_dict["youtube"],
                    "youtube",
                    latest_submissions,
                )

        logger.info("Committing changes to database")
        await db.commit()
        logger.info(
            f"Successfully saved submissions for queries: {list(all_submissions.keys())}"
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Error saving data: {e}", exc_info=True)


async def save_submissions(
    db: AsyncSession,
    search_query: str,
    submissions: List[Dict],
    source: str,
    latest_submission: Optional[datetime] = None,
):
    """Save submissions to the database depending on the source"""
    for submission in submissions:
        created_at = (
            datetime.utcfromtimestamp(submission["created"])
            if source == "reddit"
            else datetime.strptime(
                submission["created_at"], "%Y-%m-%dT%H:%M:%SZ"
            )
        )

        if latest_submission is None or created_at >= latest_submission:
            post = Posts(
                id=submission["id"],
                source=source,
                search_query=search_query,
                created_at=created_at,
                raw_data=submission,
            )
            db.add(post)


async def save_structured_output(
    search_query: str, data: Dict, db: AsyncSession
) -> Optional[StructuredOutput]:
    result = await db.execute(
        select(StructuredOutput).filter(
            StructuredOutput.search_query == search_query
        )
    )
    existing_output = result.scalar_one_or_none()
    if existing_output:
        return existing_output

    # Create StructuredOutput
    structured_output = StructuredOutput(
        search_query=search_query,
        overall_decision=data.get("overall_decision", ""),
    )

    db.add(structured_output)
    await db.commit()
    await db.refresh(structured_output)

    # Create Review records
    for review_data in data.get("reviews", []):
        review = Review(
            structured_output_id=structured_output.id, **review_data
        )
        db.add(review)

    await db.commit()
    return structured_output


async def load_structured_output(
    search_query: str, db: AsyncSession
) -> Optional[Dict]:
    """Get structured output with reviews"""

    result = await db.execute(
        select(StructuredOutput).filter(
            StructuredOutput.search_query == search_query
        )
    )
    structured_output = result.scalar_one_or_none()
    if not structured_output:
        return None

    reviews = [
        {
            "source": review.source,
            "product_name": review.product_name,
            "review_summary": review.review_summary,
            "pros": review.pros,
            "cons": review.cons,
            "sentiment": review.sentiment,
            "is_product_of_interest": review.is_product_of_interest,
            "post_id": review.post_id,
            "detail_score": review.detail_score,
            "balanced_score": review.balanced_score,
            "well_written_score": review.well_written_score,
            "url": review.url,
            "star_rating": review.star_rating,
        }
        for review in structured_output.reviews
    ]

    return {
        "id": structured_output.id,
        "search_query": structured_output.search_query,
        "overall_decision": structured_output.overall_decision,
        "reviews": reviews,
    }


async def get_existing_search_queries(db: AsyncSession) -> List[str]:
    try:
        results = await db.execute(
            select(StructuredOutput.search_query).distinct()
        )
        return [query[0] for query in results.all()]
    except Exception as e:
        logger.error(
            f"Error fetching existing search queries: {e}", exc_info=True
        )
        return []


if __name__ == "__main__":
    init_db()
