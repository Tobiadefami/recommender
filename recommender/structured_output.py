import asyncio
import json
from typing import Any, Dict, List, Optional

from langchain_openai import ChatOpenAI
from rich import print

from recommender.structured_data import AllReviewAnalysis
from recommender.task_manager import get_task_status, update_task_status


async def process_post_for_product_review(
    data: Dict[str, Any],
    search_query: str,
    source: str,
    request_id: Optional[str] = None,
) -> AllReviewAnalysis:
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.1,
    )
    structured_llm = llm.with_structured_output(AllReviewAnalysis)

    prompt = f"""
    Analyze the following {source} post and extract unique product reviews from it if and only if it is a product review.
    Indicate whether each extracted product review is a review of the product of interest: {search_query}

    post_id: {data['id']}
    post: {data['body']}
    comments: {data.get('comments', [])}
    source: {source}

    Then provide an overall decision on whether the {search_query} is a good product to buy based on the reviews extracted.
    """

    result = await structured_llm.ainvoke(prompt)
    # If we have a request_id, update the task with the new review
    if request_id:
        current_task = await get_task_status(request_id)
        if current_task and current_task.data:
            # Append new review to existing reviews
            current_data = current_task.data
            current_data["reviews"].extend(
                [
                    {
                        "source": review.source,
                        "product_name": review.product_name,
                        "review_summary": review.review_summary,
                        "pros": review.pros,
                        "cons": review.cons,
                        "sentiment": review.sentiment,
                        "is_product_of_interest": review.is_product_of_interest,
                        "post_id": review.post_id,
                        "detail_score": review.detail_score,
                        "balanced_score": review.balanced_score,
                        "well_written_score": review.well_written_score,
                        "url": review.url,
                        "star_rating": review.star_rating,
                    }
                    for review in result.reviews
                ]
            )

            await update_task_status(request_id, data=current_data)

    return result


async def batch_process_posts_for_product_review(
    data_batch: List[Dict[str, Any]],
    search_query: str,
    source: str,
    request_id: Optional[str] = None,
) -> List[AllReviewAnalysis]:
    tasks = [
        process_post_for_product_review(data, search_query, source, request_id)
        for data in data_batch
    ]
    return await asyncio.gather(*tasks)


def convert_to_dict(review_analysis: AllReviewAnalysis) -> dict[str, Any]:
    return {
        "reviews": [
            {
                "source": review.source,
                "product_name": review.product_name,
                "review_summary": review.review_summary,
                "pros": review.pros,
                "cons": review.cons,
                "sentiment": review.sentiment,
                "is_product_of_interest": review.is_product_of_interest,
                "post_id": review.post_id,
                "detail_score": review.detail_score,
                "balanced_score": review.balanced_score,
                "well_written_score": review.well_written_score,
                "url": review.url,
                "star_rating": review.star_rating,
            }
            for review in review_analysis.reviews
        ],
        "overall_decision": review_analysis.overall_decision or "",
    }


async def process_all_posts(
    data: dict,
    search_query: str,
    batch_size: int,
    request_id: Optional[str] = None,
) -> AllReviewAnalysis:
    combined_reviews = []
    overall_decisions = []

    if search_query not in data:
        return AllReviewAnalysis(
            reviews=[],
            overall_decision=None,
        )

    # initialize  task data structure if we have a request id
    if request_id:
        await update_task_status(
            request_id, data={"reviews": [], "overall_decision": None}
        )

    for source in ["reddit", "youtube"]:
        post = data[search_query][0][source]
        batches = [
            post[i : i + batch_size] for i in range(0, len(post), batch_size)
        ]
        print(
            f"batch processing search query: {search_query} for source: {source}"
        )
        for i, batch in enumerate(batches):
            results = await batch_process_posts_for_product_review(
                batch, search_query, source, request_id
            )

            for analysis in results:
                combined_reviews.extend(analysis.reviews)
                if analysis.overall_decision:
                    overall_decisions.append(analysis.overall_decision)
            # update progress based on batch completion
            if request_id:
                total_batches = (
                    sum(
                        len(data[search_query][0][s])
                        for s in ["reddit", "youtube"]
                    )
                    / batch_size
                )
                progress = (i + 1) / total_batches * 100
                await update_task_status(request_id, progress=progress)

    final_decision = None
    if overall_decisions:
        # Combine individual decisions into a final decision
        final_decision = max(
            set(overall_decisions),
            key=overall_decisions.count,
        )

    all_review_analysis = AllReviewAnalysis(
        reviews=combined_reviews,
        overall_decision=final_decision,
    )
    final_result = convert_to_dict(all_review_analysis)

    # update final result if we have a request id
    if request_id:
        await update_task_status(
            request_id, data=final_result, progress=100, status="complete"
        )
    return final_result


async def main():
    with open("data/iphone 16.json", "r") as file:
        data = json.load(file)
        processed_post = await process_all_posts(
            data,
            "iphone 16",
            batch_size=100,
        )
        print(processed_post)


if __name__ == "__main__":
    asyncio.run(main())
