from datetime import datetime
from typing import List

from asyncpraw.models import Submission

from recommender.process_comments import process_comments


async def process_submissions(
    submissions: List[Submission],
    score_threshold: int = 10,
    min_length: int = 50,
    recent_days: int | None = None,
) -> List[Submission]:
    current_time = datetime.now()
    sorted_submissions = sorted(
        submissions, key=lambda x: len(x.selftext), reverse=True
    )

    processed_submissions = []

    for submission in sorted_submissions:
        if submission.selftext.strip():
            submission_date = datetime.fromtimestamp(submission.created_utc)

            if (
                submission.score >= score_threshold
                and len(submission.selftext) >= min_length
                and (
                    not recent_days
                    or (current_time - submission_date).days <= recent_days
                )
            ):
                processed_submissions.append(submission)

    return processed_submissions


async def process_submission(
    submission,
    score_threshold=10,
    min_length=50,
    recent_days=None,
    max_comment_depth=3,
):
    # load the submission to ensure that the comments are available
    await submission.load()

    processed_comments = await process_comments(
        submission.comments,
        max_depth=max_comment_depth,
        score_threshold=score_threshold,
        min_length=min_length,
        recent_days=recent_days,
    )

    return {
        "user": submission.author.name if submission.author else "[deleted]",
        "id": submission.id,
        "title": submission.title,
        "score": submission.score,
        "url": submission.url,
        "num_comments": submission.num_comments,
        "created": submission.created,
        "body": submission.selftext,
        "comments": processed_comments,
    }
