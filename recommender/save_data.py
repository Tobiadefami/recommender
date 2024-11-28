import logging
from datetime import datetime
from typing import Dict, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from recommender.database import engine, get_db
from recommender.models import Base, Posts, Review, StructuredOutput

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    Base.metadata.create_all(bind=engine)


def save_data(all_submissions: dict):
    db: Session = next(get_db())

    try:
        for search_query, submissions_list in all_submissions.items():
            latest_submissions = (
                db.query(func.max(Posts.created_at))
                .filter(
                    func.lower(Posts.search_query) == func.lower(search_query)
                )
                .scalar()
            )
            for submission_dict in submissions_list:
                # Save Reddit submissions
                for reddit_submission in submission_dict.get("reddit", []):
                    created_at = datetime.utcfromtimestamp(
                        reddit_submission["created"]
                    )
                    if (
                        latest_submissions is None
                        or created_at >= latest_submissions
                    ):
                        post = Posts(
                            id=reddit_submission["id"],
                            source="rsseddit",
                            search_query=search_query,
                            created_at=created_at,
                            raw_data=reddit_submission,
                        )
                        db.merge(post)

                # Save YouTube submissions
                for youtube_submission in submission_dict.get("youtube", []):
                    # Use the 'published_at' field from the YouTube data
                    created_at = datetime.strptime(
                        youtube_submission["created_at"], "%Y-%m-%dT%H:%M:%SZ"
                    )
                    if (
                        latest_submissions is None
                        or created_at >= latest_submissions
                    ):
                        post = Posts(
                            id=youtube_submission["id"],
                            source="youtube",
                            search_query=search_query,
                            created_at=created_at,
                            raw_data=youtube_submission,
                        )
                        db.merge(post)

        logger.info("Committing changes to database")
        db.commit()
        logger.info(
            f"Successfully saved submissions for queries: {list(all_submissions.keys())}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving data: {e}", exc_info=True)
    finally:
        db.close()


def load_existing_data(search_query: str):
    db: Session = next(get_db())
    try:
        posts = (
            db.query(Posts)
            .filter(func.lower(Posts.search_query) == func.lower(search_query))
            .all()
        )
        reddit_posts = [
            post.raw_data for post in posts if post.source == "reddit"
        ]
        youtube_posts = [
            post.raw_data for post in posts if post.source == "youtube"
        ]
        return {
            search_query: [{"reddit": reddit_posts, "youtube": youtube_posts}]
        }
    finally:
        db.close()


def save_structured_output(
    search_query: str, data: Dict, db: Session = None
) -> Optional[StructuredOutput]:
    existing_output = (
        db.query(StructuredOutput)
        .filter(StructuredOutput.search_query == search_query)
        .first()
    )
    if existing_output:
        return existing_output

    # Create StructuredOutput
    structured_output = StructuredOutput(
        search_query=search_query,
        overall_decision=data.get("overall_decision", ""),
    )

    db.add(structured_output)
    db.commit()
    db.refresh(structured_output)

    # Create Review records
    for review_data in data.get("reviews", []):
        print(f"review_data: {review_data}")
        review = Review(
            structured_output_id=structured_output.id, **review_data
        )
        db.add(review)

    db.commit()
    return structured_output


def load_structured_output(search_query: str, db: Session = None):
    """Get structured output with reviews"""

    result = (
        db.query(StructuredOutput)
        .filter(StructuredOutput.search_query == search_query)
        .first()
    )
    if not result:
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
        for review in result.reviews
    ]

    return {
        "id": result.id,
        "search_query": result.search_query,
        "overall_decision": result.overall_decision,
        "reviews": reviews,
    }


def get_existing_search_queries():
    db: Session = next(get_db())
    try:
        queries = db.query(StructuredOutput.search_query).distinct().all()
        return [query[0] for query in queries]
    except Exception as e:
        logger.error(
            f"Error fetching existing search queries: {e}", exc_info=True
        )
        return []
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
