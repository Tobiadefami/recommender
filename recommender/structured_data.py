import json
from typing import List, Optional

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from rich import print


class ProductReviewAnalysis(BaseModel):
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
    post_id: Optional[str] = Field("the unique identifier of the post or comment")

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
    overall_decision: Optional[str] = Field(
        description="Use the data obtained from the product review analysis to provide a well detailed and an unbiased decision on whether the product is good to buy or not."
        " Highlight the top pros and cons from posts, comments and replies that have the best review scores."
    )


def process_post_for_product_review(
    post, search_query: str
) -> AllReviewAnalysis:
    llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
    structured_llm = llm.with_structured_output(AllReviewAnalysis)

    prompt = f"""
    Analyze the following post and extract product reviews from it if and only if it is a product review. Indicate whether each extracted product review is a review of the product of interest: {search_query}
    post; {post['body']}
    post_id: {post['id']}
    comments: {post['comments']}

    Then provide an overall decision on whether the {search_query} is a good product to buy based on the reviews extracted.
    """

    result = structured_llm.invoke(prompt)
    return result


def process_all_posts(
    data: dict, search_query: str, score_threshold: int = 8
) -> AllReviewAnalysis:
    combined_reviews = []
    combined_scores = []
    overall_decisions = []

    if search_query not in data:
        return AllReviewAnalysis(
            reviews = [],
            overall_decisions=None
        )
    for post in data[search_query]:
        print(f"processing search query: {search_query}")
        analysis = process_post_for_product_review(post, search_query)

        combined_reviews.extend(analysis.reviews)
        if analysis.overall_decision:
            overall_decisions.append(analysis.overall_decision)

    final_decision = None
    if overall_decisions:
        # Combine individual decisions into a final decision
        final_decision = max(
            set(overall_decisions), key=overall_decisions.count
        )

    return AllReviewAnalysis(
        reviews=combined_reviews,
        overall_decision=final_decision,
    )


if __name__ == "__main__":
    # product_output = process_text_for_product_review(
    #     "I'm currently using an iPhone XR for a little over 3 years now and it works perfectly fine with no scratches and all of its functions like Face ID working fine (other than the occasionally freezing and overheating from iOS 17.4) but I am looking for an upgrade to last me till I graduate (3-4 years from now) as I will be starting uni next year. And I am torn between getting the Base 15, 15 Pro or waiting for the Base 16. Both the 15 and 15 Pro (All Brand new) are quite cheap at the moment but there are pros and cons for each model:\n\n  \niPhone 15\n\nPros: Very affordable right now, Huge upgrade from my XR\n\nCons: Will have to use 60Hz for the next 3 years, Might be out-shadowed by the 16 coming in just 5 months\n\niPhone 15 Pro\n\nPros: 120hz, Even bigger upgrade from my XR, Potentially futureproof for the next 3 years\n\nCons: Way more expensive than the 15 (especially considering I don't care too much about its camera and don't play any games on it)\n\niPhone 16\n\nPros: Coming in just 5 months, Potentially newer/better features than the 15, More futureproof than the 15 by 1 generation.\n\nCons: More expensive than the 15 (by quite a lot since the 15 is so cheap right now), 5 months is still quite far out and don't know if my XR can hold out much longer\n\n  \nI'm also saving up for a laptop for uni so I'll save any dollar I can get but yet want a durable iPhone that can last me till I graduate. Any tips/experiences would be greatly appreciated :)\n\nPS: I don't take photos often so I don't care too much about camera quality and I also don't play any games on my phone so not too particular about performance either. Mainly just battery, durability and price are my criteria.",
    #     search_query="iphone 15",
    # )

    with open("data/reddit_data.json", "r") as file:
        data = json.load(file)
        processed_post = process_all_posts(data, "pixel 9 pro xl")
        print(processed_post)
