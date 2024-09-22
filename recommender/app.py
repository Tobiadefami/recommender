import logging
import os
import secrets

import asyncpraw
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from recommender.process_submissions import (
    process_submission,
    process_submissions,
)

CLIENT_ID = os.environ.get("REDDIT_APP_CLIENT_ID")
CLIENT_SECRET = os.environ.get("REDDIT_APP_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8000/authorize_callback"
USER_AGENT = "web:product-review-app:v1.0 (by /u/tobiadefami)"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STATE = secrets.token_urlsafe(16)

app = FastAPI()


async def get_reddit():
    reddit = asyncpraw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT,
        redirect_uri=REDIRECT_URI,
    )
    return reddit


# storage for session data
session_data = {}


@app.get("/")
async def home():
    return RedirectResponse(url="/authorize")


@app.get("/authorize")
async def authorize():
    reddit = await get_reddit()
    url = reddit.auth.url(["identity", "read"], STATE, "permanent")
    return RedirectResponse(url)


@app.get("/authorize_callback")
async def authorize_callback(request: Request):
    state = request.query_params["state"]
    code = request.query_params["code"]

    if state != STATE:
        return {"error": "State mismatch"}

    reddit = await get_reddit()
    refresh_token = await reddit.auth.authorize(code)
    session_data["refresh_token"] = refresh_token
    print("user authenticated!")
    return RedirectResponse(url="/search")


# TODO: check if the body of the submission is a product review, and if it is, search through the comments"
# determing if the text is a product review based one by passing it through a model (gemini flash or gpt-4o-mini)
# as the data gets built up from the model reviews, we can train an inexpensive model based on the data (TF-IDF)


@app.get("/search/{search_query}")
async def search(search_query: str, limit: int = 10):
    # Setup the Reddit instance using the refresh token
    if "refresh_token" not in session_data:
        return {"error": "User not authenticated."}

    # youtube_data_futures = search_youtube_videos(search_query)

    # Create a new Reddit instance for the user context
    user_reddit = asyncpraw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT,
        refresh_token=session_data["refresh_token"],
    )
    user_reddit.read_only = False
    subreddit = await user_reddit.subreddit("all")
    reddit_search_results = subreddit.search(search_query, limit=limit)

    print(f"{reddit_search_results=}")
    reddit_data = []
    async for submission in reddit_search_results:
        reddit_data.append(
            {
                "id": submission.id,
                "title": submission.title,
                "selftext": submission.selftext,
                "score": submission.score,
                "url": submission.url,
                "created_utc": submission.created_utc,
                "num_comments": submission.num_comments,
                "author": submission.author.name if submission.author else None,
            }
        )
    process_whole_reddit_data = process_submissions(reddit_data)
    processed_reddit_submissions = [
        process_submission(data, search_query=search_query)
        for data in process_whole_reddit_data
    ]

    # youtube_data = await youtube_data_futures

    all_submissions = {
        "reddit": processed_reddit_submissions,
        # "youtube": youtube_data,
    }
    # return process_all_posts(all_submissions, search_query)
    return all_submissions


if __name__ == "__main__":
    uvicorn.run(
        "recommender.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
