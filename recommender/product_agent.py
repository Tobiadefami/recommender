import logging
from typing import Dict, Optional

from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchResults
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from recommender.product_db import get_product_from_db, save_product_info

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Define the schema for the search query
class SearchQuery(BaseModel):
    query: str = Field(..., description="The search query to look up")


def get_product_information(
    query: str, model_name="gpt-4", temperature=0.1
) -> Optional[Dict]:
    existing_product = get_product_from_db(query)
    if existing_product:
        return existing_product

    ddg = DuckDuckGoSearchResults()
    llm = ChatOpenAI(model=model_name, temperature=temperature)

    def search_ddg(query) -> str:
        """Search DuckDuckGo for the given query."""
        return ddg.invoke(query)

    search_results = StructuredTool.from_function(
        func=search_ddg,
        name="search_ddg",
        description="Search the web for product information",
        args_schema=SearchQuery,
        return_direct=True,
    )

    system_message = SystemMessage(
        content="""
        You are a product specialist. Use the search tool to find factual product details about the query and return them as JSON with fields like brand, category, release_year, tier, price_range, and key_features.

        Example format:
        {
          "Product Name": {
            "brand": "Brand",
            "category": "Category",
            "release_year": 202X,
            "tier":"flasgship", "mid-range", "budget"
            "price_range": "Price Range",
            "key_features": ["Feature1", "Feature2"]
          }
        }
        """
    )

    messages = [
        system_message,
        HumanMessage(
            content=(
                f"Search the web for {query} and format it according to the structure defined."
            )
        ),
    ]

    llm_with_tools = llm.bind_tools([search_results])
    ai_msg = llm_with_tools.invoke(messages)
    messages.append(ai_msg)

    while ai_msg.tool_calls:
        for tool_call in ai_msg.tool_calls:
            selected_tool = (
                search_results if tool_call["name"] == "search_ddg" else ddg
            )

            # Convert the args to the expected format
            tool_args = {"query": query}

            tool_output = selected_tool.invoke(tool_args)
            print(f"Tool output:\n{tool_output[:200]}...")

            messages.append(
                ToolMessage(content=tool_output, tool_call_id=tool_call["id"])
            )

        ai_msg = llm_with_tools.invoke(messages)
        messages.append(ai_msg)

    print("Final output:\n", ai_msg.content)
    try:
        saved_product = save_product_info(
            product_data=ai_msg.content, raw_data=str(messages)
        )
        if saved_product:
            return ai_msg.content
        else:
            logger.error(f"Failed to save product information: {query}")
            return None
    except Exception as e:
        logger.error(f"Error in product processing: {e}")
        return None


# Example usage
if __name__ == "__main__":
    query = "lenovo legion slim 7 i 2022"
    result = get_product_information(query)
