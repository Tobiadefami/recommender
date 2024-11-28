import json
import logging
from typing import Dict, List, Optional

from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchResults
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from recommender.messages import MessageType, get_system_message
from recommender.product_agent import validate_and_clean_json_data
from recommender.product_db import save_trending_products

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CategoryQuery(BaseModel):
    category: str = Field(..., description="The product category to search for")
    timeframe: str = Field(
        ...,
        description="The timeframe to consider (e.g., 'last month', 'this year')",
    )


def get_trending_products(
    category: str,
    timeframe: str = "last month",
    model_name: str = "gpt-4",
    temperature: float = 0.1,
) -> Optional[Dict]:
    """
    Fetch trending products for a given category and timeframe.

    Args:
        category: Product category to search for
        timeframe: Time period to consider for trends
        model_name: LLM model to use
        temperature: Temperature setting for the LLM

    Returns:
        Dictionary containing trending products information
    """
    ddg = DuckDuckGoSearchResults()
    llm = ChatOpenAI(model=model_name, temperature=temperature)

    def search_trends(query: CategoryQuery) -> str:
        """Search for trending products in a category."""
        search_queries = [
            f"trending {query.category} {query.timeframe}",
            f"best selling {query.category} {query.timeframe}",
            f"most popular {query.category} reviews {query.timeframe}",
            f"top rated {query.category} {query.timeframe}",
        ]

        results = []
        for search_query in search_queries:
            results.append(ddg.invoke(search_query))

        return "\n\n".join(results)

    trend_search = StructuredTool.from_function(
        func=search_trends,
        name="search_trends",
        description="Search for trending products in a specific category",
        args_schema=CategoryQuery,
        return_direct=True,
    )

    system_message = get_system_message(MessageType.TRENDING_AGENT)
    messages = [
        SystemMessage(content=system_message),
        HumanMessage(
            content=f"Find the top 5 trending products in the {category} category for {timeframe}. "
            f"Include detailed verification from multiple sources."
        ),
    ]

    llm_with_tools = llm.bind_tools([trend_search])
    ai_msg = llm_with_tools.invoke(messages)
    messages.append(ai_msg)

    # Perform verification searches
    if ai_msg.tool_calls:
        tool_call = ai_msg.tool_calls[0]
        tool_args = {"category": category, "timeframe": timeframe}
        verification_results = trend_search.invoke(tool_args)

        messages.append(
            ToolMessage(
                content=verification_results, tool_call_id=tool_call["id"]
            )
        )

        ai_msg = llm_with_tools.invoke(messages)
        messages.append(ai_msg)

    try:
        # Clean and validate the response
        cleaned_json = validate_and_clean_json_data(ai_msg.content)
        trending_data = json.loads(cleaned_json)

        # Validate the data structure
        if not all(
            key in trending_data for key in ["category", "timeframe", "trends"]
        ):
            raise ValueError("Missing required fields in trending data")

        if not trending_data["trends"] or len(trending_data["trends"]) == 0:
            raise ValueError("No trending products found")

        # Save trending data
        saved_data = save_trending_products(
            category=category,
            timeframe=timeframe,
            trending_data=trending_data,
            raw_data=str(messages),
        )

        if saved_data:
            return trending_data
        else:
            logger.error(
                f"Failed to save trending data for category: {category}"
            )
            return None

    except Exception as e:
        logger.error(f"Error processing trending products: {e}")
        return None


def get_trending_categories() -> List[str]:
    """Return a list of supported product categories"""
    return [
        "Smartphones",
        "Laptops",
        "Gaming Consoles",
        "Headphones",
        "Smartwatches",
        "Tablets",
        "Gaming Accessories",
        "Smart Home Devices",
        "Cameras",
        "TVs",
    ]


if __name__ == "__main__":
    # Example usage
    category = "Gaming Laptops"
    timeframe = "last 3 months"
    result = get_trending_products(category, timeframe)
    if result:
        print(json.dumps(result, indent=2))
