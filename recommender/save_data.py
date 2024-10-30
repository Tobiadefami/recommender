import logging
from datetime import datetime
from typing import Any, Dict, Union

from sqlalchemy import func
from sqlalchemy.orm import Session

from recommender.database import engine, get_db
from recommender.models import Base, Posts, StructuredOutput
from recommender.structured_data import AllReviewAnalysis

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
                .filter(Posts.search_query == search_query)
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
        posts = db.query(Posts).filter(Posts.search_query == search_query).all()
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
    search_query: str, structured_data: Union[Dict[str, Any], AllReviewAnalysis]
):
    db: Session = next(get_db())

    try:
        existing_output = (
            db.query(StructuredOutput)
            .filter(StructuredOutput.search_query == search_query)
            .first()
        )
        if existing_output is None:
            structured_output = StructuredOutput(
                search_query=search_query,
                data=structured_data,
            )
            db.add(structured_output)
            db.commit()
            logger.info(f"Saved structured output for query: {search_query}")
        else:
            logger.info(
                f"Structured output for query already exists: {search_query}"
            )
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving structured output: {e}", exc_info=True)
    finally:
        db.close()


def load_structured_output(search_query: str):
    db: Session = next(get_db())
    try:
        structured_output = (
            db.query(StructuredOutput)
            .filter(StructuredOutput.search_query == search_query)
            .order_by(StructuredOutput.id.desc())
            .first()
        )
        return structured_output.data if structured_output else None
    finally:
        db.close()


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
