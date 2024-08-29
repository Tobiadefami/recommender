import json
from datetime import datetime
from typing import List


def process_post(
    data, search_query, score_threshold=10, min_length=50, recent_days=None
):
    current_time = datetime.now().timestamp()

    def process_comments(comments, score_threshold, min_length):
        processed_comments = []
        for comment in comments:
            if (
                comment["score"] >= score_threshold
                and len(comment["body"]) >= min_length
                and (
                    recent_days is None
                    or current_time - comment["created"] <= recent_days * 86400
                )
            ):
                comment_data = {
                    "author": comment["author"],
                    "body": comment["body"],
                    "score": comment["score"],
                    "created": comment["created"],
                    "replies": process_comments(
                        comment.get("replies", []), score_threshold, min_length
                    ),
                }
                processed_comments.append(comment_data)
        return processed_comments

    processed_posts = []
    for i in range(len(data[search_query])):
        post_data: dict[str, str | List[str | None]] = {
            "title": data[search_query][i]["title"],
            "body": data[search_query][i]["body"],
            "created": data[search_query][i]["created"],
            "comments": [],
        }

        post_data["comments"] = process_comments(
            data[search_query][i]["comments"], score_threshold, min_length
        )
        processed_posts.append(post_data)
    return processed_posts


if __name__ == "__main__":
    with open("data/reddit_data.json", "r") as f:
        data = json.load(f)

        post_data = process_post(data, "google pixel 9 pro xl")
        with open("data/processed_data2.json", "w") as f:
            json.dump(post_data, f, indent=2)
