import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

from exa_py import Exa
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import StructuredTool
from langchain_google_community import GoogleSearchAPIWrapper
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from recommender.messages import get_system_message
from recommender.product_db import (
    get_product_from_db,
    save_product_info,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

exa = Exa(api_key=os.getenv("EXA_API_KEY"))

SEARCH_ENGINE_MAP = {
    "google": GoogleSearchAPIWrapper(),
    "ddg": DuckDuckGoSearchRun(),
    "exa": exa,
}


class SearchQuery(BaseModel):
    query: str = Field(..., description="The search query to look up")


class CategoryQuery(BaseModel):
    category: str = Field(..., description="The product category to search for")
    timeframe: str = Field(
        ...,
        description="The timeframe to consider (e.g., 'last month', 'this year')",
    )


class Agent:
    def __init__(
        self,
        model_name: str = "gpt-4o",
        temperature: float = 0.1,
        information_type: str = "product",
        search_engine_name: str = "ddg",
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.information_type = information_type
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        self.current_year = datetime.now().year
        self.search_engine_name = search_engine_name

    async def _validate_and_clean_json_data(self, json_string: str) -> str:
        """Clean and validate json string before parsing"""
        if json_string.startswith("```json"):
            json_string = json_string.split("```json")[1]
        if json_string.endswith("```"):
            json_string = json_string.split("```")[0]
        return json_string.strip()

    def _search_product(self, query: str) -> Optional[str]:
        """Search for specific product information"""
        enhanced_query = f"{query} specs technical details official reviews"

        if (
            self.search_engine_name == "google"
            or self.search_engine_name == "ddg"
        ):
            return SEARCH_ENGINE_MAP[self.search_engine_name].run(
                enhanced_query
            )
        elif self.search_engine_name == "exa":
            return SEARCH_ENGINE_MAP[
                self.search_engine_name
            ].search_and_contents(
                enhanced_query,
                use_autoprompt=True,
                num_results=2,
                text=True,
                highlights=True,
            )

    async def get_search_tool(self) -> StructuredTool:
        """Get appropriate search tool based on information type"""
        return StructuredTool.from_function(
            func=self._search_product,
            name="search_product",
            description="Search the web for product information",
            args_schema=SearchQuery,
            return_direct=True,
        )

    async def get_information(self, query: str) -> Optional[Dict]:
        """Main method to get information based on type"""
        return await self._get_product_information(query)

    async def _get_product_information(self, query: str) -> Optional[Dict]:
        """Handle product information retrieval"""
        existing_product = await get_product_from_db(query)
        if existing_product:
            return existing_product

        search_tool = await self.get_search_tool()
        messages = await self._initialize_messages(query)
        return await self._process_information(messages, search_tool, query)

    async def _initialize_messages(self, query: str) -> List:
        """Initialize message chain based on information type"""

        system_message = get_system_message(current_year=self.current_year)

        content = (
            f"Search for detailed and verified information about {query}. "
            "Focus on official sources and reliable reviews."
        )

        return [
            SystemMessage(content=system_message),
            HumanMessage(content=content),
        ]

    async def _process_information(
        self,
        messages: List,
        search_tool: StructuredTool,
        query: str,
        timeframe: Optional[str] = None,
    ) -> Optional[Dict]:
        """Process and validate information"""
        llm_with_tools = self.llm.bind_tools([search_tool])
        ai_msg = llm_with_tools.invoke(messages)
        messages.append(ai_msg)

        iteration = 0
        max_iterations = 2

        while ai_msg.tool_calls and iteration < max_iterations:
            tool_output = await self._handle_tool_calls(
                ai_msg, search_tool, query, timeframe
            )
            messages.append(
                ToolMessage(
                    content=tool_output, tool_call_id=ai_msg.tool_calls[0]["id"]
                )
            )

            ai_msg = llm_with_tools.invoke(messages)
            messages.append(ai_msg)
            iteration += 1

        return await self._save_information(ai_msg, messages, query, timeframe)

    async def _handle_tool_calls(
        self,
        ai_msg,
        search_tool: StructuredTool,
        query: str,
        timeframe: Optional[str] = None,
    ) -> str:
        """Handle tool calls based on information type"""
        verification_queries = [
            f"{query} official specifications",
            f"{query} official release date and price",
            f"{query} official reviews",
        ]
        results = []
        for v_query in verification_queries:
            result = search_tool.invoke({"query": v_query})
            results.append(f"--- Results for {v_query} ---\n{result}")
        return "\n".join(results)

    async def _save_information(
        self,
        ai_msg,
        messages: List,
        query: str,
        timeframe: Optional[str] = None,
    ) -> Optional[Dict]:
        """Save and validate information based on type"""
        try:
            cleaned_json = await self._validate_and_clean_json_data(
                ai_msg.content
            )
            data = json.loads(cleaned_json)
            logger.info(data)
            if self.information_type == "product":
                return await save_product_info(
                    product_data=ai_msg.content, raw_data=str(messages)
                )

        except Exception as e:
            logger.error(f"Error processing information: {e}")
            return None
