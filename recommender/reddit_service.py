import logging
import secrets
from typing import Tuple

import asyncpraw
from fastapi import HTTPException
from sqlalchemy.orm import Session

from recommender.environment_vars import (
    CLIENT_ID,
    CLIENT_SECRET,
    REDIRECT_URI,
    USER_AGENT,
)
from recommender.models import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RedditService:
    def __init__(self, db: Session):
        self.db = db

    async def get_reddit_client(self):
        return asyncpraw.Reddit(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            user_agent=USER_AGENT,
            redirect_uri=REDIRECT_URI,
        )

    async def get_auth_url(self, user: User) -> Tuple[str, str]:
        """Generate Reddit OAuth URL for user authentication"""

        reddit = await self.get_reddit_client()
        state = secrets.token_urlsafe(16)

        # Store state in the user model
        user.reddit_state = state
        self.db.commit()

        auth_url = reddit.auth.url(["identity", "read"], state, "permanent")
        return str(auth_url), state

    async def handle_callback(self, code: str, state: str, user: User) -> bool:
        """Handle Reddit OAuth callback to save app credentials"""

        # Verify state matches user's stored state
        if user.reddit_state != state:
            raise HTTPException(status_code=403, detail="Invalid state")

        reddit = await self.get_reddit_client()

        try:
            refresh_token = await reddit.auth.authorize(code)

            # Store directly on user record
            user.reddit_refresh_token = refresh_token
            user.has_reddit_refresh_token = True
            user.reddit_state = (
                None  # clear the state after successful authentication
            )

            self.db.commit()
            return True

        except Exception as e:
            logger.error(f"Reddit Authentication failed: {str(e)}")
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def get_authorized_client(self, user: User):
        """Get Reddit client with user's refresh token"""
        reddit = await self.get_reddit_client()
        if not user.has_reddit_refresh_token:
            logger.warning(
                f"User {user.username} does not have a refresh token"
            )
            return reddit

        try:
            reddit = asyncpraw.Reddit(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                user_agent=USER_AGENT,
                refresh_token=user.reddit_refresh_token,
            )
            return reddit
        except Exception as e:
            logger.error(f"Failed to authorize user {user.username}: {str(e)}")
            return await self.get_reddit_client()
