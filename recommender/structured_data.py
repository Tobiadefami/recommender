from langchain_openai import ChatOpenAI
from langchain_google_vertexai import ChatVertexAI
from langchain_core.pydantic_v1 import BaseModel, Field
from pydantic.v1.types import OptionalIntFloatDecimal
import vertexai
import os
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from typing import Optional, List
from google.api_core.exceptions import ResourceExhausted
from rich import print
# vertexai.init()

class ProductReviewAnalysis(BaseModel):
    product_name: Optional[str] = Field(description="The name of the product being reviewed, if applicable")
    review_summary: Optional[str] = Field(description="A brief summary of the review, if it is a product review")
    sentiment: Optional[str] = Field(description="The sentiment of the review (positive, negative, neutral), if it is a product review")
    is_product_of_interest: bool = Field(description="Whether the review is a review of the product of interest")

class ProductScore(BaseModel):
    detail_score: int = Field(
        description=(
            "The detail score of the review from 0-10 (0 means the review is poorly"
            " detailed and 10 means it is very well detailed), if it is a product review")
    )
    balanced_score: int= Field(
        description=(
            "The balanced score of the review from 0-10 (0 means the review is biased"
            " and 10 means it is very balanced), if it is a product review")
    )
    well_written_score: int = Field(description=(
        "The well-written score of the review from 0-10 (0 means the review is poorly written and 10 means it is very well written),"
        " if it is a product review")
    )


class AllReviewAnalysis(BaseModel):
    reviews: List[ProductReviewAnalysis] = Field(description="A list of product review analysis for all reviews. If no reviews are present an empty list is returned")
    scores: List[ProductScore] = Field(description="A list of scores for each review,")

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=retry_if_exception_type((ResourceExhausted, Exception))
)
def process_text_for_product_review(text: str, search_query: str) -> AllReviewAnalysis:
    llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
    structured_llm = llm.with_structured_output(AllReviewAnalysis)

    prompt = f"""
    Analyze the following post and extract product reviews from it. Indicate whether each extracted product review is a review of the product of interest: {search_query}
    post: {text}
    """

    result = structured_llm.invoke(prompt)
    return result




if __name__ == "__main__":
    product_output = process_text_for_product_review("I'm currently using an iPhone XR for a little over 3 years now and it works perfectly fine with no scratches and all of its functions like Face ID working fine (other than the occasionally freezing and overheating from iOS 17.4) but I am looking for an upgrade to last me till I graduate (3-4 years from now) as I will be starting uni next year. And I am torn between getting the Base 15, 15 Pro or waiting for the Base 16. Both the 15 and 15 Pro (All Brand new) are quite cheap at the moment but there are pros and cons for each model:\n\n  \niPhone 15\n\nPros: Very affordable right now, Huge upgrade from my XR\n\nCons: Will have to use 60Hz for the next 3 years, Might be out-shadowed by the 16 coming in just 5 months\n\niPhone 15 Pro\n\nPros: 120hz, Even bigger upgrade from my XR, Potentially futureproof for the next 3 years\n\nCons: Way more expensive than the 15 (especially considering I don't care too much about its camera and don't play any games on it)\n\niPhone 16\n\nPros: Coming in just 5 months, Potentially newer/better features than the 15, More futureproof than the 15 by 1 generation.\n\nCons: More expensive than the 15 (by quite a lot since the 15 is so cheap right now), 5 months is still quite far out and don't know if my XR can hold out much longer\n\n  \nI'm also saving up for a laptop for uni so I'll save any dollar I can get but yet want a durable iPhone that can last me till I graduate. Any tips/experiences would be greatly appreciated :)\n\nPS: I don't take photos often so I don't care too much about camera quality and I also don't play any games on my phone so not too particular about performance either. Mainly just battery, durability and price are my criteria.",
     search_query="iphone 15")


    print(product_output)
