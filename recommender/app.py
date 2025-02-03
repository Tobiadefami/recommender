import logging
from datetime import timedelta

import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse

from recommender.analytics import (
    format_analytics_result,
    get_user_search_analytics,
)
from recommender.auth import (
    authenticate_user,
    create_access_token,
    create_user,
    get_current_user,
)
from recommender.database import get_db, init_db
from recommender.environment_vars import ORIGIN, REDIRECT_URL
from recommender.fetch_youtube_data import search_youtube_videos
from recommender.models import (
    SearchHistory,
    User,
)
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
)
from recommender.schemas import SearchAnalytic, UserCreate, UserResponse
from recommender.structured_output import process_all_posts
from recommender.utils import autocomplete, filter_data

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
    await init_db()


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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check Reddit authentication status"""
    user = await db.execute(select(User).filter(User.id == current_user.id))
    user = user.scalar_one_or_none()
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
    db: AsyncSession = Depends(get_db),
):
    """Deactivate Reddit connection for the current user"""
    user = await db.execute(select(User).filter(User.id == current_user.id))
    user = user.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Clear Reddit-related fields
    user.has_reddit_refresh_token = False
    user.reddit_refresh_token = None
    user.reddit_state = None
    await db.commit()

    return {"detail": "Reddit connection successfully deactivated"}


@app.get("/user/recent-searches", response_model=list[SearchAnalytic])
async def get_recent_searches(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 3,
):
    """get users most recent searches with analytics"""
    analytics = await get_user_search_analytics(current_user.id, db, limit)
    return format_analytics_result(analytics)


# Authentication endpoints
@app.post("/register")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await create_user(db, user.username, user.email, user.password)
    return user


@app.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
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
    db: AsyncSession = Depends(get_db),
):
    """Initialize Reddit authentication process for app-level access"""
    reddit_service = RedditService(db)
    auth_url, _ = await reddit_service.get_auth_url(current_user)
    return {"url": auth_url}


@app.get("/reddit/callback")
async def reddit_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
):
    """Handle Reddit OAuth callback"""

    user = await db.execute(select(User).filter(User.reddit_state == state))
    user = user.scalar_one_or_none()
    reddit_service = RedditService(db)

    success = await reddit_service.handle_callback(code, state, user)

    redirect_url = REDIRECT_URL
    if success:
        return RedirectResponse(url=f"{redirect_url}")

    return RedirectResponse(url=f"{redirect_url}?reddit_auth=failed")


@app.get("/autocomplete")
async def auto_complete(query: str, db: AsyncSession = Depends(get_db)):
    existing_queries = await get_existing_search_queries(db)

    return await autocomplete(query, existing_queries)


@app.get("/similar_products/{product_name}")
async def similar_products(
    product_name: str, _: User = Depends(get_current_user)
):
    """
    Get similar products to the given product name.
    Returns an empty list if no similar products are found.
    """
    if not product_name or len(product_name.strip()) == 0:
        raise HTTPException(
            status_code=400, detail="Product name cannot be empty."
        )

    logger.info(f"Searching for similar products for: {product_name}")
    normalized_product_name = product_name.lower()

    product_catalogue = ProductCatalogue()
    await product_catalogue.initialize()

    similar_products = await product_catalogue.get_similar_product(
        normalized_product_name
    )
    logger.info(f"{similar_products=}")
    return {"similar_products": similar_products}


@app.get("/search/{search_query}")
async def search(
    search_query: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 2,
    batch_size: int = 20,
    skip_history: bool = Header(False, alias="X-Skip-History"),
):
    normalized_query = search_query.lower()

    try:
        results = await _execute_main_search(
            normalized_query, current_user, db, limit, batch_size, skip_history
        )
        return results
    except Exception as e:
        logger.error(f"Search Error: {str(e)}")
        return {
            "reviews": [],
            "overall_decision": "An error occurred while processing your search.",
            "similar_products": {
                "same_brand": [],
                "competitors": [],
                "similar_category": [],
            },
        }


async def _execute_main_search(
    query, current_user, db, limit, batch_size, skip_history
):
    try:
        # Check cache first
        structured_output = await load_structured_output(query, db=db)
        if structured_output:
            if not skip_history:
                await _update_search_history(
                    current_user, query, structured_output, db
                )
            return filter_data(structured_output)

        # Initialize services
        reddit_service = RedditService(db=db)
        reddit_search_results = []

        try:
            reddit = await reddit_service.get_authorized_client(current_user)
            subreddit = await reddit.subreddit("all")
            async for submission in subreddit.search(query, limit=limit):
                reddit_search_results.append(submission)
        except Exception as e:
            logger.error(f"Reddit API error: {str(e)}")
            # Continue with empty results if Reddit fails

        # Get YouTube data
        try:
            youtube_data = await search_youtube_videos(query, max_results=limit)
        except Exception as e:
            logger.error(f"YouTube API error: {str(e)}")
            youtube_data = []

        # Process results
        process_whole_reddit_data = await process_submissions(
            reddit_search_results
        )
        processed_reddit_submissions = [
            await process_submission(data) for data in process_whole_reddit_data
        ]

        all_submissions = {
            query: [
                {
                    "reddit": processed_reddit_submissions,
                    "youtube": youtube_data,
                }
            ]
        }

        await save_data(all_submissions, db=db)
        results = await process_all_posts(all_submissions, query, batch_size)
        filtered_results = filter_data(results)

        if not skip_history:
            await _update_search_history(
                current_user, query, filtered_results, db
            )

        return filtered_results

    except Exception as e:
        logger.error(f"Error in main search execution: {str(e)}", exc_info=True)
        # Return empty results structure instead of failing
        return {
            "reviews": [],
            "overall_decision": "Unable to fetch results at this time.",
            "similar_products": {
                "same_brand": [],
                "competitors": [],
                "similar_category": [],
            },
        }


async def _update_search_history(current_user, query, structured_output, db):
    try:
        # First await the execute
        result = await db.execute(
            select(SearchHistory).filter(
                SearchHistory.user_id == current_user.id,
                SearchHistory.search_query == query,
            )
        )
        # Then get the scalar result
        existing_history = await result.scalar_one_or_none()

        if not existing_history:
            search_history = SearchHistory(
                user_id=current_user.id,
                search_query=query,
                structured_output_id=structured_output["id"],
            )
            db.add(search_history)
            await db.commit()
    except Exception as e:
        logger.error(f"Error updating search history: {str(e)}")
        await db.rollback()


@app.get("/user/search-analytics", response_model=list[SearchAnalytic])
async def get_user_search_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get analytics for the current user's search history"""
    analytics = await get_user_search_analytics(current_user.id, db)
    return format_analytics_result(analytics)


if __name__ == "__main__":
    uvicorn.run(
        "recommender.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
