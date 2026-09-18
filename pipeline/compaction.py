"""Convert the conversation into structured facts consumed by the tools."""

import re

from config import (
    DEFAULT_PRIORITY,
    ISSUE_EXTRACTION_PATTERNS,
    PRIORITY_PATTERN,
    QUOTED_QUERY_PATTERN,
)
from llm.client import complete_support_request
from pipeline.state import CompactedTicketInfo, SessionState

SYSTEM_PROMPT = """You convert an employee IT support conversation into a compact,
structured request. Read the full conversation and extract exactly these
fields as a JSON object, no markdown fences, no commentary.

Routing rules:
- Treat the latest user request as the active request.
- Assistant clarification questions and the user's answers to them provide context only.
- Use knowledge_search for guidance, instructions, requirements, troubleshooting, or how-to questions.
- Use ticket_creation only when the user explicitly asks to create, open, or submit a support ticket.
- Use ticket_lookup only when the user asks about an existing ticket or its status.
- Extract the user's actual problem when clearly described; do not include employee ID or ticket instructions.
- Leave issue_summary empty when a ticket request has no described problem or a lookup has no ticket ID or issue reference.
- Preserve the user's priority wording exactly; validation rejects unsupported values.
- For quoted knowledge queries, extract only the quoted text.

{
  "issue_summary": string,
  "intent": "knowledge_search" | "ticket_lookup" | "ticket_creation" | "other",
  "employee_id": string | null,
  "ticket_id": string | null,
  "category": string | null,
  "priority": string,
  "info_complete": boolean,
  "missing_fields": [string]
}
"""


def _format_transcript(history: list) -> str:
    return "\n".join(f"{message['role']}: {message['content']}" for message in history)


def _quoted_query(request: str) -> str | None:
    match = re.search(QUOTED_QUERY_PATTERN, request)
    return match.group(1).strip() if match else None


def _request_issue(request: str) -> str | None:
    for pattern in ISSUE_EXTRACTION_PATTERNS:
        match = re.search(pattern, request, flags=re.IGNORECASE)
        if match:
            issue = match.group(1).strip(" .,")
            if issue and "ticket" not in issue.lower():
                return issue
    return None


def _explicit_priority(request: str) -> str | None:
    match = re.search(PRIORITY_PATTERN, request, flags=re.IGNORECASE)
    return match.group(1).lower() if match else None


def run(state: SessionState) -> SessionState:
    transcript = _format_transcript(state["conversation_history"])
    if state.get("active_request"):
        transcript = f"Active request: {state['active_request']}\n\n{transcript}"

    result = complete_support_request(SYSTEM_PROMPT, transcript)
    user_messages = [
        message["content"]
        for message in state["conversation_history"]
        if message["role"] == "user"
    ]
    active_request = user_messages[-1] if user_messages else state.get("active_request", "")
    parsed_issue = _request_issue(active_request)

    if result.get("intent") == "ticket_lookup" and not result.get("ticket_id") and parsed_issue:
        result["issue_summary"] = parsed_issue
    elif result.get("intent") == "ticket_creation":
        if parsed_issue:
            result["issue_summary"] = parsed_issue
        result["priority"] = _explicit_priority(active_request) or DEFAULT_PRIORITY
    elif result.get("intent") == "knowledge_search":
        quoted_query = _quoted_query(active_request)
        if quoted_query is not None:
            result["issue_summary"] = quoted_query
        elif not result.get("issue_summary", "").strip() and state.get("active_request"):
            result["issue_summary"] = state["active_request"]

    state["compacted_info"] = CompactedTicketInfo(**result)
    return state
