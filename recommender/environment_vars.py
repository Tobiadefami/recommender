import os

CLIENT_ID = os.environ.get("REDDIT_APP_CLIENT_ID")
CLIENT_SECRET = os.environ.get("REDDIT_APP_CLIENT_SECRET")
NGINX_HOST = os.getenv("NGINX_HOST")
RECOMMENDER_ENV = os.getenv("RECOMMENDER_ENV", "development")
PROTOCOL = "http" if RECOMMENDER_ENV == "development" else "https"
REDIRECT_URI = f"{PROTOCOL}://{NGINX_HOST}/api/reddit/callback"
USER_AGENT = "web:product-review-app:v1.0 (by /u/tobiadefami)"
REDIRECT_URL = f"{PROTOCOL}://{NGINX_HOST}"
ORIGIN = [REDIRECT_URL]
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://user:password@db/recommender_db"
)
