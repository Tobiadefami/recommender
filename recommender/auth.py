from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from recommender.database import get_db
from recommender.environment_vars import JWT_SECRET_KEY
from recommender.models import User

# Configuration
SECRET_KEY = JWT_SECRET_KEY
ALGORITHM = "HS256"


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user_by_username(db, username)

    if user is None:
        raise credentials_exception
    return user


async def get_user_by_username(
    db: AsyncSession, username: str
) -> Optional[User]:
    """Get user by username"""
    user = await db.execute(select(User).filter(User.username == username))
    return user.scalar_one_or_none()


async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> Optional[User]:
    """Authenticate user"""
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def create_user(
    db: AsyncSession, username: str, email: str, password: str
) -> User:
    "Create a new user"

    # check if user already exists in the db
    existing_user = await get_user_by_username(db, username)

    if existing_user:
        raise HTTPException(
            status_code=400, detail="Username already registered"
        )

    hashed_password = get_password_hash(password)
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        is_active=True,
    )
    try:
        db.add(user)
        await db.flush()
        await db.commit()
        return user
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500, detail=f"failed to create user: {e}"
        )


async def update_user(db: AsyncSession, user: User) -> User:
    """Update user information in database"""
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
