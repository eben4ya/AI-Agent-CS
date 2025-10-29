from __future__ import annotations

from functools import lru_cache
from typing import Any, Iterable, List, Literal, TypedDict

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from .llm import get_chat_model
from .prompts import build_agent_prompt
from .tools import get_agent_tools


class ConversationTurn(TypedDict):
    role: Literal["user", "assistant"]
    content: str


def _format_history(history: Iterable[ConversationTurn]) -> List[BaseMessage]:
    """Convert serialized history into LangChain message objects."""
    formatted: List[BaseMessage] = []
    for turn in history:
        role = turn.get("role")
        content = turn.get("content", "")
        if not content:
            continue
        if role == "assistant":
            formatted.append(AIMessage(content=content))
        else:
            formatted.append(HumanMessage(content=content))
    return formatted


@lru_cache(maxsize=1)
def get_agent_executor() -> AgentExecutor:
    """Instantiate and cache the tool-calling agent executor."""
    llm = get_chat_model()
    tools = get_agent_tools()
    prompt = build_agent_prompt()
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=False, handle_parsing_errors=True)


async def run_agent(
    customer_message: str,
    *,
    conversation_history: Iterable[ConversationTurn] | None = None,
    store_profile: str = "",
    catalog_context: str = "",
) -> dict[str, Any]:
    """Execute the agent with the given customer message, history, and context."""
    executor = get_agent_executor()
    inputs = {
        "customer_message": customer_message,
        "conversation_history": _format_history(conversation_history or []),
        "store_profile": store_profile or "",
        "catalog_context": catalog_context or "",
    }
    result = await executor.ainvoke(inputs)
    return {
        "reply": result.get("output", ""),
        "intermediate_steps": result.get("intermediate_steps", []),
    }


__all__ = ["ConversationTurn", "get_agent_executor", "run_agent"]
