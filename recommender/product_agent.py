import json
import logging
from datetime import datetime
from typing import Dict, Optional

from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchResults
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from recommender.messages import get_system_message
from recommender.product_db import get_product_from_db, save_product_info

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Define the schema for the search query
class SearchQuery(BaseModel):
    query: str = Field(..., description="The search query to look up")


def validate_and_clean_json_data(json_string: str) -> str:
    """Clean and validate json string before parsing"""

    if json_string.startswith("```json"):
        json_string = json_string.split("```json")[1]
    if json_string.endswith("```"):
        json_string = json_string.split("```")[0]

    # Remove any leading/trailing whitespace
    json_string = json_string.strip()
    return json_string


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
        enhanced_query = f"{query} specs technical details official reviews"
        return ddg.invoke(enhanced_query)

    search_results = StructuredTool.from_function(
        func=search_ddg,
        name="search_ddg",
        description="Search the web for product information",
        args_schema=SearchQuery,
        return_direct=True,
    )
    current_year = datetime.now().year

    system_message = SystemMessage(content=get_system_message(current_year))

    messages = [
        system_message,
        HumanMessage(
            content=(
                f"Search for detailed and verified information about {query}. "
                "Focus on oficcial sources and reliable reviews."
            )
        ),
    ]

    llm_with_tools = llm.bind_tools([search_results])
    ai_msg = llm_with_tools.invoke(messages)
    messages.append(ai_msg)

    iteration = 0
    max_iterations = 3

    while ai_msg.tool_calls and iteration < max_iterations:
        for tool_call in ai_msg.tool_calls:
            if tool_call["name"] == "search_ddg":
                verification_queries = [
                    f"{query} official specifications",
                    f"{query} official release date and price",
                    f"{query} official reviews",
                ]

                tool_output = ""
                for v_query in verification_queries:
                    # Convert the args to the expected format
                    tool_args = {"query": v_query}
                    result = search_results.invoke(tool_args)
                    tool_output += (
                        f"\n--- Results for {v_query} ---\n{result}\n"
                    )
                    print(f"Tool output:\n{tool_output[:200]}...")

                messages.append(
                    ToolMessage(
                        content=tool_output, tool_call_id=tool_call["id"]
                    )
                )

        ai_msg = llm_with_tools.invoke(messages)
        messages.append(ai_msg)
        iteration += 1
    logger.info(f"Completed {iteration} iterations")

    print("Final output:\n", ai_msg.content)

    try:
        # validate the product format and content
        cleaned_json = validate_and_clean_json_data(ai_msg.content)
        logger.info(f"Cleaned Json Data  : {cleaned_json}")
        try:
            product_info = json.loads(cleaned_json)
        except json.JSONDecodeError as json_error:
            logger.error(f"Error in parsing JSON data: {json_error}")
            logger.error(f"Problematic JSON data: {cleaned_json}")
            return None
        logger.info(f"Parsed product info: {product_info}")

        for product in product_info.values():
            if product["release_year"] > current_year:
                raise ValueError(
                    "Release year can not be greater than the current year"
                )
            if not all(
                key in product for key in ["brand", "model", "confidence_score"]
            ):
                raise ValueError(
                    "Missing required fields in product information"
                )

        saved_product = save_product_info(
            product_data=ai_msg.content, raw_data=str(messages)
        )
        if saved_product:
            return ai_msg.content
        else:
            logger.error(f"Failed to save product information: {query}")
            return None
    except Exception as e:
        logger.error(f"Error in processing product information: {e}")
        return None


# Example usage
if __name__ == "__main__":
    query = "lenovo legion slim 7 i 2022"
    result = get_product_information(query)
