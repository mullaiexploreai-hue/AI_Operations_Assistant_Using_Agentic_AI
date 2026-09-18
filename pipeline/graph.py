"""LangGraph orchestration for the AI Operations Assistant."""

from langgraph.graph import END, StateGraph

from config import DEFAULT_CATEGORY, LOGGER, SUPPORTED_PRIORITIES
from pipeline import compaction, info_gathering
from pipeline.state import RequestIntent, SessionState, now_iso
from session import session_store
from tools.support_tools import create_ticket, lookup_ticket, search_knowledge_base


def _route_after_gathering(state: SessionState) -> str:
    return "continue"


def _select_tool(state: SessionState) -> SessionState:
    state["selected_tool"] = state["compacted_info"].intent.value
    return state


def _validate_request(state: SessionState) -> SessionState:
    info = state["compacted_info"]
    missing = []
    if info.intent == RequestIntent.TICKET_LOOKUP:
        if not info.employee_id:
            missing.append("employee ID")
        if not info.ticket_id and not info.issue_summary.strip():
            missing.append("ticket ID or issue description")
    elif info.intent == RequestIntent.TICKET_CREATION:
        if not info.employee_id:
            missing.append("employee ID")
        if not info.issue_summary.strip():
            missing.append("issue description")
    elif info.intent == RequestIntent.KNOWLEDGE_SEARCH and not info.issue_summary.strip():
        missing.append("question")
    if info.intent == RequestIntent.TICKET_CREATION and info.priority not in SUPPORTED_PRIORITIES:
        missing.append("valid priority")
    if missing:
        state["awaiting_clarification"] = True
        state["conversation_history"].append({
            "role": "assistant",
            "content": f"Please provide: {', '.join(dict.fromkeys(missing))}.",
            "timestamp": now_iso(),
        })
    else:
        state["awaiting_clarification"] = False
    return state


def _route_after_validation(state: SessionState) -> str:
    return "end" if state["awaiting_clarification"] else "continue"


def _knowledge_search_node(state: SessionState) -> SessionState:
    query = state["compacted_info"].issue_summary
    result = search_knowledge_base(query)
    state["tool_calls"].append({
        "tool": "search_knowledge_base",
        "args": {"query": query},
        "result": result,
    })
    state["tool_result"] = result
    return state


def _ticket_lookup_node(state: SessionState) -> SessionState:
    info = state["compacted_info"]
    result = lookup_ticket(info.ticket_id, info.employee_id, info.issue_summary)
    state["tool_calls"].append({
        "tool": "lookup_ticket",
        "args": {
            "ticket_id": info.ticket_id,
            "employee_id": info.employee_id,
            "issue_summary": info.issue_summary,
        },
        "result": result,
    })
    state["tool_result"] = result
    return state


def _ticket_creation_node(state: SessionState) -> SessionState:
    info = state["compacted_info"]
    result = create_ticket(
        info.employee_id or "",
        info.issue_summary,
        info.category or DEFAULT_CATEGORY,
        info.priority,
    )
    state["tool_calls"].append({
        "tool": "create_ticket",
        "args": {
            "employee_id": info.employee_id,
            "issue_summary": info.issue_summary,
            "category": info.category,
            "priority": info.priority,
        },
        "result": result,
    })
    state["tool_result"] = result
    return state


def _final_response_node(state: SessionState) -> SessionState:
    info = state["compacted_info"]
    result = state["tool_result"] or {}
    selected_tool = state["selected_tool"]
    if result.get("duplicate"):
        reply = f"I did not create a duplicate. An open matching ticket already exists: {result['ticket_id']}."
    elif result.get("error"):
        reply = f"I couldn't complete that request: {result['error']}"
    elif selected_tool == RequestIntent.KNOWLEDGE_SEARCH.value:
        if result.get("found"):
            article = result["results"][0]
            reply = f"I found this guidance in {article['source']}, {article['title']}: {article['content']}"
        else:
            reply = "I couldn't find a matching IT knowledge article. You can ask me to create a support ticket instead."
    elif selected_tool == RequestIntent.TICKET_LOOKUP.value:
        if result.get("found"):
            ticket = result["ticket"]
            reply = f"Ticket {ticket['ticket_id']} is {ticket['status']}. Summary: {ticket['issue_summary']}. Priority: {ticket['priority']}."
        else:
            reply = f"I couldn't find ticket {info.ticket_id or 'that ticket'} for the supplied employee details."
    elif selected_tool == RequestIntent.TICKET_CREATION.value:
        if result.get("created"):
            reply = f"Your IT ticket {result['ticket_id']} has been created with {result['status']} status."
        else:
            reply = f"I couldn't create the ticket: {result.get('error', 'the tool returned an unknown error')}"
    else:
        reply = "I can search IT guidance, look up an existing ticket, or create a new ticket. Which would you like?"
    state["conversation_history"].append({"role": "assistant", "content": reply, "timestamp": now_iso()})
    return state


def _build_graph():
    graph = StateGraph(SessionState)
    graph.add_node("info_gathering", info_gathering.run)
    graph.add_node("compaction", compaction.run)
    graph.add_node("validate_request", _validate_request)
    graph.add_node("select_tool", _select_tool)
    graph.add_node("knowledge_search", _knowledge_search_node)
    graph.add_node("ticket_lookup", _ticket_lookup_node)
    graph.add_node("ticket_creation", _ticket_creation_node)
    graph.add_node("final_response", _final_response_node)
    graph.set_entry_point("info_gathering")
    graph.add_conditional_edges("info_gathering", _route_after_gathering, {"end": END, "continue": "compaction"})
    graph.add_edge("compaction", "validate_request")
    graph.add_conditional_edges("validate_request", _route_after_validation, {"end": END, "continue": "select_tool"})
    graph.add_conditional_edges(
        "select_tool",
        lambda state: state["selected_tool"],
        {
            RequestIntent.KNOWLEDGE_SEARCH.value: "knowledge_search",
            RequestIntent.TICKET_LOOKUP.value: "ticket_lookup",
            RequestIntent.TICKET_CREATION.value: "ticket_creation",
            RequestIntent.OTHER.value: "final_response",
        },
    )
    graph.add_edge("knowledge_search", "final_response")
    graph.add_edge("ticket_lookup", "final_response")
    graph.add_edge("ticket_creation", "final_response")
    graph.add_edge("final_response", END)
    return graph.compile()


_compiled_graph = _build_graph()


def run_customer_turn(session_id: str, user_message: str) -> SessionState:
    state = session_store.get_or_create_session(session_id)
    state["request_continued"] = bool(state.get("awaiting_clarification") and state.get("active_request"))
    if not state["request_continued"]:
        state["active_request"] = user_message
    state["conversation_history"].append({"role": "user", "content": user_message, "timestamp": now_iso()})
    state["turn_count"] += 1
    try:
        result_state = _compiled_graph.invoke(state)
    except Exception:
        LOGGER.exception("Customer turn failed", extra={"session_id": session_id})
        state["conversation_history"].append({
            "role": "assistant",
            "content": "I couldn't complete that request right now. Please try again or contact IT support.",
            "timestamp": now_iso(),
        })
        state["tool_result"] = {"ok": False, "error": "The assistant workflow is temporarily unavailable."}
        result_state = state
    session_store.save_session(session_id, result_state)
    return result_state
