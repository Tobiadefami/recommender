import logging
from datetime import datetime

from sqlalchemy import func

from recommender.database import engine, get_db
from recommender.models import Base, Posts
from recommender.process_submissions import (
    process_submission,
    process_submissions,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


Base.metadata.create_all(bind=engine)


def save_data(submissions, search_query):
    db = next(get_db())
    # get the lastest submission data for this search query
    latest_submission = (
        db.query(func.max(Posts.created_at))
        .filter(Posts.search_query == search_query)
        .scalar()
    )
    try:
        processed_reddit_submissions = process_submissions(
            submissions["reddit"]
        )
        logger.info(f"processed {len(processed_submissions)} submissions")
        new_submissions_count = 0
        for submission in processed_submissions:
            processed_data = process_submission(submission, search_query)
            created_at = datetime.utcfromtimestamp(processed_data["created"])

            # Logic to check if we need to save the current submission:
            # If there's no previous submission (latest_submission is None), we save it.
            # If the current submission is newer or equal to the latest saved submission,
            # we save it to ensure we don't miss any updates.
            if latest_submission is None or created_at >= latest_submission:
                post = RedditPost(
                    id=processed_data["id"],
                    search_query=search_query,
                    created_at=created_at,
                    data=processed_data,
                )
                logger.info(f"Attempting to save post ID: {post.id}")
                db.merge(post)  # This will insert or update
                logger.info(f"Post with ID {post.id} merged")
                new_submissions_count += 1

        logger.info("Committing changes to database")
        db.commit()
        logger.info(
            f"Successfully saved {new_submissions_count} new posts for query: {search_query}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving data: {e}", exc_info=True)
    finally:
        db.close()


def load_existing_data(search_query):
    db = next(get_db())
    try:
        posts = (
            db.query(RedditPost)
            .filter(RedditPost.search_query == search_query)
            .all()
        )
        return {search_query: [post.data for post in posts]}
    finally:
        db.close()


# The following functions are no longer needed with the database approach:
# - load_existing_data (from file)
# - add_new_submissions
# - save_updated_data (to file)
