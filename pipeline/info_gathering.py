"""First graph node: gather the minimum facts required for an IT action.

Job of this node, and *only* this node: look at the full conversation and
decide whether there's enough information to act. If not, produce a single
clarifying question and stop the turn there. It deliberately does NOT
produce the structured `CompactedTicketInfo` — that's the Context
Compaction node's job (pipeline/compaction.py). Keeping these separate is
the teaching point: "enough info to proceed?" and "what exactly is the
structured ticket?" are different questions, and conflating them into one
LLM call makes both harder to prompt for and to test.
"""
from pipeline.state import SessionState, now_iso

SYSTEM_PROMPT = """You are the information-gathering step of an internal IT support assistant.

Read the full conversation so far and decide whether enough information has
been gathered to route this request to the correct IT tool. Do not solve the
issue yourself — only judge completeness and, if incomplete, ask ONE
clarifying question.

Minimum information required:
- Knowledge search: a clear question.
- Ticket lookup: employee ID and ticket ID, or employee ID plus a clear issue reference.
- Ticket creation: employee ID and a clear issue description.

Routing guidance:
- Treat the latest user request as the active request.
- Assistant questions and answers to them are context only.
- A request for information, instructions, requirements, or troubleshooting
    is complete for knowledge search; it does not require an employee ID.
- A clear question remains complete even when the topic may have no article.
    For example, "How do I reserve a parking space?" must proceed to the
    knowledge search so the assistant can return a no-match result.
- Do not interpret the word "request" as ticket creation unless the user
    explicitly asks to create, open, or submit a ticket.

If the customer has provided enough detail for their apparent issue type,
mark it complete even if some of the above fields are technically implicit
(e.g. they only have one order and it's obvious which one they mean).

Respond with ONLY a JSON object, no markdown fences, no commentary:
{
  "info_complete": true | false,
  "clarifying_question": string | null   // required if info_complete is false, else null
}
"""


def _format_transcript(history: list) -> str:
    lines = [f"{m['role']}: {m['content']}" for m in history]
    return "\n".join(lines)


def run(state: SessionState) -> SessionState:
    """Preserve the turn for structured extraction and deterministic validation.

    Completeness is decided after compaction, when the request intent and
    extracted fields are available. This node deliberately does not ask the
    LLM to make a second, independent completeness decision.
    """
    state["awaiting_clarification"] = False
    return state
