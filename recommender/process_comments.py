from datetime import datetime

from asyncpraw.models import Comment


async def process_comments(
    comment_forest,
    depth=0,
    max_depth=3,
    score_threshold=10,
    min_length=50,
    recent_days=None,
):
    if depth >= max_depth:
        return []

    processed_comments = []
    current_time = datetime.now()

    async for comment in comment_forest:
        if isinstance(comment, Comment):
            comment_data = {
                "author": comment.author.name
                if comment.author
                else "[deleted]",
                "id": comment.id,
                "body": comment.body,
                "score": comment.score,
                "created": comment.created,
                "url": f"https://www.reddit.com{comment.permalink}",
                "replies": [],
            }

            comment_date = datetime.fromtimestamp(comment.created_utc)

            if (
                comment.score >= score_threshold
                and len(comment.body) >= min_length
                and (
                    not recent_days
                    or (current_time - comment_date).days <= recent_days
                )
            ):
                comment_data["replies"] = await process_comments(
                    comment.replies,
                    depth + 1,
                    max_depth,
                    score_threshold,
                    min_length,
                    recent_days,
                )
                processed_comments.append(comment_data)

    return sorted(
        processed_comments,
        key=lambda x: x["score"],
        reverse=True,
    )
