from typing import Literal

from agents import Agent, ModelSettings, WebSearchTool
from constants import DEFAULT_AGENT_MODEL

default_search_context: Literal["low", "medium", "high"] = "medium"


async def build_research_agent() -> Agent:
    search_tool = WebSearchTool(search_context_size=default_search_context)

    agent = Agent(
        name="Research Agent",
        instructions=(
            "You are a research agent. Always use the web search tool and never invent information."
        ),
        tools=[search_tool],
        model_settings=ModelSettings(
            tool_choice="required",
            temperature=0,
        ),
        model=DEFAULT_AGENT_MODEL,
    )
    return agent

