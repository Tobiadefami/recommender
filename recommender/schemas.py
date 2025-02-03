from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class ReviewBase(BaseModel):
    source: str
    product_name: str
    review_summary: str
    pros: List[str]
    cons: List[str]
    sentiment: Optional[str] = None
    is_product_of_interest: bool
    post_id: str
    detail_score: float
    balanced_score: float
    well_written_score: float
    url: str
    star_rating: Optional[float] = None


class Review(ReviewBase):
    id: int
    structured_output_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class StructuredOutputBase(BaseModel):
    search_query: str
    overall_decision: Optional[str] = None


class StructuredOutput(StructuredOutputBase):
    id: int
    created_at: datetime
    updated_at: datetime
    reviews: List[Review]

    class Config:
        from_attributes = True


class SearchHistoryItem(BaseModel):
    search_query: str
    searched_at: datetime
    structured_output: Optional[StructuredOutput] = None

    class Config:
        from_attributes = True


class SearchAnalytic(BaseModel):
    query: str
    timestamp: datetime
    resultCount: int
    averageRating: float
    sentiment: str

    class Config:
        from_attributes = True


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    has_reddit_refresh_token: bool
    search_history: List[SearchHistoryItem] = []

    class Config:
        from_attributes = True
