import asyncio
import json
from typing import Any, Dict, List

from langchain_openai import ChatOpenAI
from rich import print

from recommender.structured_data import AllReviewAnalysis


async def process_post_for_product_review(
    data: Dict[str, Any], search_query: str, source: str
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
    return result


async def batch_process_posts_for_product_review(
    data_batch: List[Dict[str, Any]],
    search_query: str,
    source: str,
) -> List[AllReviewAnalysis]:
    tasks = [
        process_post_for_product_review(data, search_query, source)
        for data in data_batch
    ]
    return await asyncio.gather(*tasks)


async def process_all_posts(
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
            results = await batch_process_posts_for_product_review(
                batch, search_query, source
            )

            for analysis in results:
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
