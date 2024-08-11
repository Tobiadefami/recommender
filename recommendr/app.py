import praw
from fastapi import FastAPI, Request, Depends
import os
from fastapi.responses import RedirectResponse
import secrets
import uvicorn
import logging
from datetime import datetime
from save_data import save_reddit_data

CLIENT_ID = os.environ.get('REDDIT_APP_CLIENT_ID')
CLIENT_SECRET = os.environ.get('REDDIT_APP_CLIENT_SECRET')
REDIRECT_URI = "http://localhost:8000/authorize_callback"
USER_AGENT = "web:product-review-app:v1.0 (by /u/tobiadefami)"

STATE = secrets.token_urlsafe(16)

app = FastAPI()

reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT,
    redirect_uri=REDIRECT_URI)


# storage for session data
session_data = {}

@app.get("/")
def home():
    return RedirectResponse(url="/authorize")

@app.get("/authorize")
def authorize():
    url = reddit.auth.url(["identity", "read"], STATE, "permanent")
    return RedirectResponse(url)

@app.get("/authorize_callback")
def authorize_callback(request: Request):
    state = request.query_params["state"]
    code = request.query_params["code"]

    if state != STATE:
        return {"error": "State mismatch"}

    refresh_token = reddit.auth.authorize(code)
    session_data["refresh_token"] = refresh_token
    print("user authenticated!")
    return RedirectResponse(url="/search")


# TODO: check if the body of the submission is a product review, and if it is, search through the comments"
# determing if the text is a product review based one by passing it through a model (gemini flash or gpt-4o-mini)
# as the data gets built up from the model reviews, we can train an inexpensive model based on the data (TF-IDF)

@app.get('/search/{search_query}')
def search(search_query: str = "sonya7rv", limit: int = 10):
    if 'refresh_token' not in session_data:
        return {"error": "User not authenticated."}

    # Setup the Reddit instance using the refresh token
    if 'refresh_token' not in session_data:
        return {"error": "User not authenticated."}

    # Create a new Reddit instance for the user context
    user_reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT,
        refresh_token=session_data['refresh_token']
    )
    user_reddit.read_only = False

    submissions = list(user_reddit.subreddit('all').search(search_query, limit=limit))
    # save the data
    save_reddit_data(submissions, search_query)
    results = []
    for submission in user_reddit.subreddit('all').search(search_query, limit=limit):
        submmision_data = {
            'search_query': search_query,
            'id': submission.id,
            'title': submission.title,
            'score': submission.score,
            'url': submission.url,
            'num_comments': submission.num_comments,
            'created': submission.created,
            'body': submission.selftext
        }
        results.append(submmision_data)
        logging.info([type(x) for x in submmision_data.values()])


    return results

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
