from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.messages import BaseMessage

from .types import ConversationTurn


class ConversationMemoryStore:
    """Store chat histories keyed by session, using LangChain message objects."""

    def __init__(self) -> None:
        self._store: Dict[str, BaseChatMessageHistory] = {}

    def get_history(self, session_id: str) -> BaseChatMessageHistory:
        """Return (and lazily create) the chat history for a session."""
        if session_id not in self._store:
            self._store[session_id] = InMemoryChatMessageHistory()
        return self._store[session_id]

    def get_turns(self, session_id: str) -> List[ConversationTurn]:
        """Return the conversation turns in a serialisable form for the agent."""
        history = self.get_history(session_id)
        turns: List[ConversationTurn] = []
        for message in history.messages:
            if message.type == "human":
                turns.append({"role": "user", "content": message.content})
            elif message.type == "ai":
                turns.append({"role": "assistant", "content": message.content})
        return turns

    def append_user_message(self, session_id: str, content: str) -> None:
        self.get_history(session_id).add_user_message(content)

    def append_ai_message(self, session_id: str, content: str) -> None:
        self.get_history(session_id).add_ai_message(content)

    def load_messages(self, session_id: str) -> List[BaseMessage]:
        """Return the raw LangChain message objects for advanced usage/testing."""
        return list(self.get_history(session_id).messages)

    def clear_session(self, session_id: str) -> None:
        self._store.pop(session_id, None)

    def clear_all(self) -> None:
        self._store.clear()


default_memory_store = ConversationMemoryStore()


def get_conversation_turns(session_id: str, store: Optional[ConversationMemoryStore] = None) -> List[ConversationTurn]:
    """Convenience helper to retrieve conversation turns for the agent input."""
    return (store or default_memory_store).get_turns(session_id)


__all__ = [
    "ConversationMemoryStore",
    "default_memory_store",
    "get_conversation_turns",
]
