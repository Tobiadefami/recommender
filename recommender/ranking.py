from typing import List, Tuple
from google.cloud.aiplatform_v1beta1.types.notebook_euc_config import NotebookEucConfig
from langchain_core.load.load import Reviver
from langchain_core.pydantic_v1 import BaseModel, Field
from recommender.structured_data import process_text_for_product_review
from langchain_google_vertexai import ChatVertexAI
import json
from pathlib import Path


class ReviewSummary(BaseModel):
    summary: str
    detail_score: int
    balanced_score: int
    well_written_score: int
    sentiment: str
    is_product_review: bool

class ProsCons(BaseModel):
    pros: List[str]
    cons: List[str]

def get_top_reviews(reviews:List[str], search_query: str, num_reviews:int=5) -> List[ReviewSummary]:

    summaries = []
    for review in reviews:
        review, score = process_text_for_product_review(review, search_query)
        summary = ReviewSummary(
            is_product_review = review.is_product_review,
            summary = review.review_summary,
            detail_score = score.detail_score,
            balanced_score = score.balanced_score,
            well_written_score = score.well_written_score,
            sentiment = review.sentiment)
        summaries.append(summary)

    # sort summaries based on score
    sorted_summaries = sorted(summaries, key=lambda x: x.detail_score + x.balanced_score + x.well_written_score, reverse=True)
    return sorted_summaries[:num_reviews]

def extract_pro_cons(reviews:List[ReviewSummary]) -> ProsCons:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)
    structured_llm = llm.with_structured_output(ProsCons)
    reviews_text = "\n".join([f"{review.summary} {review.sentiment}" for review in reviews])
    prompt = f"""
    Based on the following reviews, extract the pros and cons of the product:

    {reviews_text}
    Provide a list of pros and cons for the product.
    """

    result = structured_llm.invoke(prompt)
    return result

def get_overall_sentiment(reviews: List[ReviewSummary]) -> str:
    sentiment = [review.sentiment for review in reviews]
    positive = sentiment.count("positive")
    negative = sentiment.count("negative")
    neutral = sentiment.count("neutral")

    if positive > negative and positive > neutral:
        return "Positive"
    elif negative > positive and negative > neutral:
        return "Negative"
    else:
        return "Neutral"


def process_document(document: List[str], search_query: str) -> Tuple[List[ReviewSummary], ProsCons, str]:
    top_reviews = get_top_reviews(document, search_query)
    pros_cons = extract_pro_cons(top_reviews)
    overall_sentiment = get_overall_sentiment(top_reviews)

    return top_reviews, pros_cons, overall_sentiment

def format_data(data_dir:Path)->List[str]:
    extracted_data = []
    with open(data_dir, 'r') as f:
        data = json.load(f)
        for item in data:
            body = item['body']
            extracted_data.append(body)
    print(f"{len(extracted_data)=}")
    return extracted_data

if __name__ == "__main__":
    data_dir = Path("data/reddit_data.json")
    # search_query = "google pixel 7 pro"
    document = format_data(data_dir)
    reviews, pros_cons, sentiment = process_document(document, search_query)

    print("Top Reviews:")
    for review in reviews:
        print(f"- {review.summary} (Detail: {review.detail_score}, Balance: {review.balanced_score}, Writing: {review.well_written_score})")

    print("\nPros:")
    for pro in pros_cons.pros:
        print(f"- {pro}")

    print("\nCons:")
    for con in pros_cons.cons:
        print(f"- {con}")

    print(f"\nOverall Sentiment: {sentiment}")
