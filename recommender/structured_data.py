from typing import List, Optional

from pydantic import BaseModel, Field


class ProductReviewAnalysis(BaseModel):
    source: str = Field(
        description="The source of the review (reddit or youtube)"
    )
    product_name: Optional[str] = Field(
        description="The name of the product being reviewed, if applicable"
    )
    review_summary: Optional[str] = Field(
        description="A brief summary of the review, if it is a product review"
    )
    pros: Optional[List[str]] = Field("list the various pros of the product")
    cons: Optional[List[str]] = Field("list the various cons of the product")
    sentiment: Optional[str] = Field(
        description="The sentiment of the review (positive, negative, neutral), if it is a product review"
    )
    is_product_of_interest: bool = Field(
        description="Whether the review is a review of the product of interest"
    )
    post_id: Optional[str] = Field(
        "the unique identifier of the post or comment from reddit or youtube"
    )

    detail_score: int = Field(
        description=(
            "The detail score of the review from 0-10 (0 means the review is poorly"
            " detailed and 10 means it is very well detailed), if it is a product review"
        )
    )
    balanced_score: int = Field(
        description=(
            "The balanced score of the review from 0-10 (0 means the review is biased"
            " and 10 means it is very balanced), if it is a product review"
        )
    )
    well_written_score: int = Field(
        description=(
            "The well-written score of the review from 0-10 (0 means the review is poorly written and 10 means it is very well written),"
            " if it is a product review"
        )
    )


class AllReviewAnalysis(BaseModel):
    reviews: List[ProductReviewAnalysis] = Field(
        description="A list of product review analysis for all reviews. If no reviews are present an empty list is returned"
    )
    overall_decision: str = Field(
        description="Use the data obtained from the product review analysis to provide a well detailed and an unbiased decision on whether the product is good to buy or not."
        " List the top pros and cons, comments and replies that have the best review scores."
    )
