import json
import logging
import os
import secrets
from typing import Dict

import asyncpraw
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from recommender.auto_complete import autocomplete
from recommender.database import init_db
from recommender.fetch_youtube_data import search_youtube_videos
from recommender.process_submissions import (
    process_submission,
    process_submissions,
)
from recommender.product_catalogue import ProductCatalogue
from recommender.save_data import (
    get_existing_search_queries,
    load_structured_output,
    save_data,
    save_structured_output,
)
from recommender.structured_output import process_all_posts

CLIENT_ID = os.environ.get("REDDIT_APP_CLIENT_ID")
CLIENT_SECRET = os.environ.get("REDDIT_APP_CLIENT_SECRET")
NGINX_HOST = os.getenv("NGINX_HOST")
RECOMMENDER_ENV = os.getenv("RECOMMENDER_ENV", "development")
PROTOCOL = "http" if RECOMMENDER_ENV == "development" else "https"
REDIRECT_URI = f"{PROTOCOL}://{NGINX_HOST}/api/authorize_callback"
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
def auto_complete(query: str):
    existing_queries = get_existing_search_queries()

    return autocomplete(query, existing_queries)


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
    return RedirectResponse(url="/")


@app.get("/similar_products/{product_name}")
def similar_products(product_name: str):
    normalized_product_name = product_name.lower()
    product_catalogue = ProductCatalogue()
    similar_products = product_catalogue.get_similar_product(
        normalized_product_name
    )
    if any(similar_products.values()):
        return {
            "similar_products": similar_products,
        }
    return {"error": "Product not found or no similar products available."}


def filter_data(db: Dict[str, list[dict]]) -> Dict[str, list[dict]]:
    modified = [
        data for data in db["reviews"] if data.get("review_summary") is not None
    ]
    db["reviews"] = modified
    return db


@app.get("/search/{search_query}")
async def search(search_query: str, limit: int = 2, batch_size: int = 20):
    refresh_token = load_refresh_token()

    if not refresh_token:
        return {"error": "User not authenticated."}

    normalized_query = search_query.lower()

    existing_result = load_structured_output(normalized_query)
    if existing_result is not None:
        print(f"{existing_result=}")
        return filter_data(existing_result)

    youtube_data_futures = search_youtube_videos(
        normalized_query, max_results=limit
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

    async for submission in subreddit.search(normalized_query, limit=limit):
        reddit_search_results.append(submission)

    process_whole_reddit_data = await process_submissions(reddit_search_results)
    processed_reddit_submissions = [
        await process_submission(data) for data in process_whole_reddit_data
    ]

    youtube_data = await youtube_data_futures
    all_submissions = {
        normalized_query: [
            {"reddit": processed_reddit_submissions, "youtube": youtube_data}
        ]
    }

    save_data(all_submissions)
    results = await process_all_posts(
        all_submissions, normalized_query, batch_size
    )
    filtered_results = filter_data(results)
    save_structured_output(normalized_query, filtered_results)
    return filtered_results


if __name__ == "__main__":
    uvicorn.run(
        "recommender.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
