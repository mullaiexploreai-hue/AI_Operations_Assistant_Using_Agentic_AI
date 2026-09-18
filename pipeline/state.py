"""State models shared by the IT Operations Assistant graph."""
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict

from pydantic import BaseModel, Field


def now_iso() -> str:
    """Single source of truth for message timestamps."""
    return datetime.now(timezone.utc).isoformat()


class RequestIntent(str, Enum):
    KNOWLEDGE_SEARCH = "knowledge_search"
    TICKET_LOOKUP = "ticket_lookup"
    TICKET_CREATION = "ticket_creation"
    OTHER = "other"


class CompactedTicketInfo(BaseModel):
    """Structured facts passed from language understanding to tools."""

    issue_summary: str
    intent: RequestIntent
    employee_id: Optional[str] = None
    ticket_id: Optional[str] = None
    category: Optional[str] = None
    priority: str = "medium"
    info_complete: bool
    missing_fields: List[str] = Field(default_factory=list)


class SessionState(TypedDict):
    """State retained across turns and passed through one graph invocation."""

    session_id: str
    conversation_history: List[Dict[str, Any]]
    active_request: Optional[str]
    request_continued: bool
    compacted_info: Optional[CompactedTicketInfo]
    selected_tool: Optional[str]
    tool_calls: List[Dict[str, Any]]
    tool_result: Optional[Dict[str, Any]]
    turn_count: int
    awaiting_clarification: bool


def new_session_state(session_id: str) -> SessionState:
    """Factory for a brand-new, empty session."""
    return SessionState(
        session_id=session_id,
        conversation_history=[],
        active_request=None,
        request_continued=False,
        compacted_info=None,
        selected_tool=None,
        tool_calls=[],
        tool_result=None,
        turn_count=0,
        awaiting_clarification=False,
    )
