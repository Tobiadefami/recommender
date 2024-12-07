import logging
from datetime import timedelta

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from recommender.analytics import (
    format_analytics_result,
    get_user_search_analytics,
)
from recommender.auth import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from recommender.auto_complete import autocomplete
from recommender.database import get_db, init_db
from recommender.environment_vars import ORIGIN, REDIRECT_URL
from recommender.fetch_youtube_data import search_youtube_videos
from recommender.models import SearchHistory, User
from recommender.process_submissions import (
    process_submission,
    process_submissions,
)
from recommender.product_catalogue import ProductCatalogue
from recommender.reddit_service import RedditService
from recommender.save_data import (
    get_existing_search_queries,
    load_structured_output,
    save_data,
    save_structured_output,
)
from recommender.schemas import SearchAnalytic, UserCreate, UserResponse
from recommender.structured_output import process_all_posts
from recommender.trending_agent import (
    get_trending_categories,
    get_trending_products,
)
from recommender.utils import filter_data

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

ACCESS_TOKEN_EXPIRE_MINUTES = 30


@app.on_event("startup")
async def startup_event():
    init_db()


@app.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )
    return current_user


@app.get("/reddit/status")
async def reddit_status(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Check Reddit authentication status"""
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "connected": user.has_reddit_refresh_token,
        "username": user.reddit_username,
        "lastSync": user.reddit_last_sync,
    }


@app.post("/reddit/deactivate")
async def deactivate_reddit(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Deactivate Reddit connection for the current user"""
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Clear Reddit-related fields
    user.has_reddit_refresh_token = False
    user.reddit_refresh_token = None
    user.reddit_state = None
    db.commit()

    return {"detail": "Reddit connection successfully deactivated"}


@app.get("/user/recent-searches", response_model=list[SearchAnalytic])
async def get_recent_searches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 3,
):
    """get users most recent searches with analytics"""
    analytics = get_user_search_analytics(current_user.id, db, limit)
    return format_analytics_result(analytics)


# Authentication endpoints
@app.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_active=True,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/reddit/auth")
async def reddit_auth(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Initialize Reddit authentication process for app-level access"""
    reddit_service = RedditService(db)
    auth_url, _ = await reddit_service.get_auth_url(current_user)
    return {"url": auth_url}


@app.get("/reddit/callback")
async def reddit_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db),
):
    """Handle Reddit OAuth callback"""

    user = db.query(User).filter(User.reddit_state == state).first()
    reddit_service = RedditService(db)

    success = await reddit_service.handle_callback(code, state, user)

    redirect_url = REDIRECT_URL
    if success:
        return RedirectResponse(url=f"{redirect_url}")

    return RedirectResponse(url=f"{redirect_url}?reddit_auth=failed")


@app.get("/autocomplete")
def auto_complete(query: str):
    existing_queries = get_existing_search_queries()

    return autocomplete(query, existing_queries)


@app.get("/similar_products/{product_name}")
def similar_products(product_name: str):
    if not product_name or len(product_name.strip()) == 0:
        raise HTTPException(status_code=400, detail="Product name cannot be empty.")
    logger.info(f"Searching for similar products for: {product_name}")
    normalized_product_name = product_name.lower()
    product_catalogue = ProductCatalogue()
    similar_products = product_catalogue.get_similar_product(normalized_product_name)
    if not similar_products:
        raise HTTPException(
            status_code=404,
            detail="Product not found or no similar products available.",
        )

    return {"similar_products": similar_products}


@app.get("/trending/{category}")
async def get_trending(
    category: str,
    timeframe: str = "last month",
    current_user: User = Depends(get_current_user),
):
    """Get trending products for a specific category"""
    result = get_trending_products(category, timeframe)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"No trending products found for category: {category}",
        )
    return result


@app.get("/trending-categories")
async def get_categories():
    """Get list of supported product categories"""
    return {"categories": get_trending_categories()}


@app.get("/search/{search_query}")
async def search(
    search_query: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 2,
    batch_size: int = 20,
):
    normalized_query = search_query.lower()

    # Get existing structured output from database
    structured_output = load_structured_output(normalized_query, db=db)
    existing_search_history = (
        db.query(SearchHistory)
        .filter(
            SearchHistory.user_id == current_user.id,
            SearchHistory.search_query == normalized_query,
        )
        .first()
    )
    # If we have cached results
    if structured_output:
        if not existing_search_history:
            # Create search history entry with the existing structured output
            search_history = SearchHistory(
                user_id=current_user.id,
                search_query=search_query,
                structured_output_id=structured_output["id"],
            )
            db.add(search_history)
            db.commit()

            # Return cached results
        return filter_data(structured_output)

    # If no cached results, perform new search
    reddit_service = RedditService(db=db)
    reddit = await reddit_service.get_authorized_client(current_user)

    youtube_data_futures = search_youtube_videos(normalized_query, max_results=limit)

    subreddit = await reddit.subreddit("all")
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
    results = await process_all_posts(all_submissions, normalized_query, batch_size)
    filtered_results = filter_data(results)

    # Save structured output and create search history
    structured_output = save_structured_output(
        normalized_query, filtered_results, db=db
    )
    if structured_output and not existing_search_history:
        search_history = SearchHistory(
            user_id=current_user.id,
            search_query=search_query,
            structured_output_id=structured_output.id,
        )
        db.add(search_history)
        db.commit()

    return filtered_results


@app.get("/user/search-analytics", response_model=list[SearchAnalytic])
async def get_user_search_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get analytics for the current user's search history"""
    analytics = get_user_search_analytics(current_user.id, db)
    return format_analytics_result(analytics)


if __name__ == "__main__":
    uvicorn.run(
        "recommender.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
