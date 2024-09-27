import json
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from rich import print


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
    overall_decision: Optional[str] = Field(
        description="Use the data obtained from the product review analysis to provide a well detailed and an unbiased decision on whether the product is good to buy or not."
        " Highlight the top pros and cons from posts, comments and replies that have the best review scores."
    )


def process_post_for_product_review(
    data: Dict[str, Any], search_query: str, source: str
) -> AllReviewAnalysis:
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.1,
    )
    structured_llm = llm.with_structured_output(AllReviewAnalysis)

    prompt = f"""
    Analyze the each of the following {source} post and extract unique product reviews from it if and only if it is a product review.
    Indicate whether each extracted product review is a review of the product of interest: {search_query}

    post_id: {data['id']}
    post: {data['body']}
    comments: {data.get('comments', [])}
    source: {source}

    Then provide an overall decision on whether the {search_query} is a good product to buy based on the reviews extracted.
    """

    result = structured_llm.invoke(prompt)
    return result


def batch_process_posts_for_product_review(
    data_batch: List[Dict[str, Any]],
    search_query: str,
    source: str,
    num_threads: int,
) -> AllReviewAnalysis:
    results = []
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [
            executor.submit(
                process_post_for_product_review, data, search_query, source
            )
            for data in data_batch
        ]
        for future in futures:
            result = future.result()
            results.append(result)
    return results


def process_all_posts(
    data: dict, search_query: str, batch_size: int
) -> AllReviewAnalysis:
    combined_reviews = []
    overall_decisions = []

    if search_query not in data:
        return AllReviewAnalysis(
            reviews=[],
            overall_decision=None,
        )

    for source in ["reddit", "youtube"]:
        post = data[search_query][0][source]
        batches = [
            post[i : i + batch_size] for i in range(0, len(post), batch_size)
        ]

        print(
            f"batch processing search query: {search_query} for source: {source}"
        )
        for batch in batches:
            result = batch_process_posts_for_product_review(
                batch, search_query, source, num_threads=12
            )

            for analysis in result:
                combined_reviews.extend(analysis.reviews)
                if analysis.overall_decision:
                    overall_decisions.append(analysis.overall_decision)

    final_decision = None
    if overall_decisions:
        # Combine individual decisions into a final decision
        final_decision = max(
            set(overall_decisions),
            key=overall_decisions.count,
        )

    return AllReviewAnalysis(
        reviews=combined_reviews,
        overall_decision=final_decision,
    )


if __name__ == "__main__":
    with open(
        "data/iphone 16.json",
        "r",
    ) as file:
        data = json.load(file)
        processed_post = process_all_posts(
            data,
            "iphone 16",
            batch_size=20,
        )
        print(processed_post)
