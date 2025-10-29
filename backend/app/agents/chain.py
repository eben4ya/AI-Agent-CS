from __future__ import annotations

from functools import lru_cache
from typing import Any, Iterable, List

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from .llm import get_chat_model
from .prompts import build_agent_prompt
from .tools import get_agent_tools
from .memory import default_memory_store, ConversationMemoryStore
from .types import ConversationTurn


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
    session_id: str | None = None,
    memory_store: ConversationMemoryStore | None = None,
) -> dict[str, Any]:
    """Execute the agent with the given customer message, history, and context."""
    executor = get_agent_executor()
    history_turns = conversation_history
    if history_turns is None and session_id:
        store = memory_store or default_memory_store
        history_turns = store.get_turns(session_id)

    inputs = {
        "customer_message": customer_message,
        "conversation_history": _format_history(history_turns or []),
        "store_profile": store_profile or "",
        "catalog_context": catalog_context or "",
    }
    result = await executor.ainvoke(inputs)
    reply = result.get("output", "")

    if session_id:
        store = memory_store or default_memory_store
        store.append_user_message(session_id, customer_message)
        if reply:
            store.append_ai_message(session_id, reply)

    return {
        "reply": reply,
        "intermediate_steps": result.get("intermediate_steps", []),
    }


__all__ = ["ConversationTurn", "get_agent_executor", "run_agent"]
