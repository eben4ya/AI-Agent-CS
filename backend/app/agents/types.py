from __future__ import annotations

from typing import Literal, TypedDict


class ConversationTurn(TypedDict):
    role: Literal["user", "assistant"]
    content: str


__all__ = ["ConversationTurn"]
