import json
import logging
import os
import secrets

import asyncpraw
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from recommender.database import init_db
from recommender.fetch_youtube_data import search_youtube_videos
from recommender.process_submissions import (
    process_submission,
    process_submissions,
)
from recommender.save_data import save_data, save_structured_output
from recommender.structured_output import process_all_posts

CLIENT_ID = os.environ.get("REDDIT_APP_CLIENT_ID")
CLIENT_SECRET = os.environ.get("REDDIT_APP_CLIENT_SECRET")
NGINX_HOST = os.getenv("NGINX_HOST")
RECOMMENDER_ENV = os.getenv("RECOMMENDER_ENV", "development")
PROTOCOL = "http" if RECOMMENDER_ENV == "development" else "https"
print(f"{PROTOCOL=}")
REDIRECT_URI = f"{PROTOCOL}://{NGINX_HOST}/api/authorize_callback"
print(f"{REDIRECT_URI=}")
USER_AGENT = "web:product-review-app:v1.0 (by /u/tobiadefami)"

STATE = secrets.token_urlsafe(16)
REFRESH_TOKEN_FILE = "refresh_token.json"

ORIGIN = [f"{PROTOCOL}://{NGINX_HOST}"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGIN,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    init_db()


async def get_reddit():
    reddit = asyncpraw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT,
        redirect_uri=REDIRECT_URI,
    )
    return reddit


def save_refresh_token(token):
    with open(REFRESH_TOKEN_FILE, "w") as f:
        json.dump({"refresh_token": token}, f)


def load_refresh_token():
    if os.path.exists(REFRESH_TOKEN_FILE):
        with open(REFRESH_TOKEN_FILE, "r") as f:
            data = json.load(f)
            return data.get("refresh_token")
    return None


@app.get("/")
async def home():
    return RedirectResponse(url="/authorize")


@app.get("/autocomplete")
def auto_complete(query: str, queries_db=None):
    return auto_complete(query, queries_db)


@app.get("/authorize")
async def authorize():
    reddit = await get_reddit()
    url = reddit.auth.url(["identity", "read"], STATE, "permanent")
    return RedirectResponse(url=str(url))


@app.get("/authorize_callback")
async def authorize_callback(request: Request):
    state = request.query_params["state"]
    code = request.query_params["code"]

    if state != STATE:
        return {"error": "State mismatch"}

    reddit = await get_reddit()
    refresh_token = await reddit.auth.authorize(code)
    save_refresh_token(refresh_token)
    print("user authenticated!")
    return RedirectResponse(url="/search")


@app.get("/search/{search_query}")
async def search(search_query: str, limit: int = 5, batch_size: int = 20):
    refresh_token = load_refresh_token()
    if not refresh_token:
        return {"error": "User not authenticated."}

    youtube_data_futures = search_youtube_videos(
        search_query, max_results=limit
    )

    user_reddit = asyncpraw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT,
        refresh_token=refresh_token,
    )
    user_reddit.read_only = False
    subreddit = await user_reddit.subreddit("all")
    reddit_search_results = []

    async for submission in subreddit.search(search_query, limit=limit):
        reddit_search_results.append(submission)

    process_whole_reddit_data = await process_submissions(reddit_search_results)
    processed_reddit_submissions = [
        await process_submission(data) for data in process_whole_reddit_data
    ]

    youtube_data = await youtube_data_futures
    all_submissions = {
        search_query: [
            {"reddit": processed_reddit_submissions, "youtube": youtube_data}
        ]
    }
    save_data(all_submissions)
    results = await process_all_posts(all_submissions, search_query, batch_size)
    save_structured_output(search_query, results)
    return results


if __name__ == "__main__":
    uvicorn.run(
        "recommender.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
