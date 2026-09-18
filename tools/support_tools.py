"""SQLite-backed support tools exposed to the IT Operations Assistant."""

import re
import sqlite3
import uuid
from datetime import datetime, timezone

from config import (
    ACTIVE_TICKET_STATUSES,
    DEFAULT_CATEGORY,
    DEFAULT_PRIORITY,
    LOGGER,
    MAX_KNOWLEDGE_RESULTS,
    MIN_MATCHED_SEARCH_TERMS,
    MIN_SEARCH_TOKEN_LENGTH,
    SUPPORTED_PRIORITIES,
)
from db.connection import ensure_initialized, get_admin_connection, get_read_only_connection


def _tool_error(message: str) -> dict:
    LOGGER.error(message)
    return {"ok": False, "error": message}


def search_knowledge_base(query: str) -> dict:
    """Search local IT articles using token overlap and prefix matching."""
    terms = [
        term
        for term in re.findall(r"[a-z0-9]+", query.lower())
        if len(term) >= MIN_SEARCH_TOKEN_LENGTH
    ]
    if not terms:
        return {"found": False, "results": []}

    conn = None
    try:
        conn = get_read_only_connection()
        rows = conn.execute(
            "SELECT article_id, title, content, source, keywords FROM knowledge_articles"
        ).fetchall()
        results = []
        for row in rows:
            text = " ".join((row["title"], row["content"], row["keywords"])).lower()
            tokens = re.findall(r"[a-z0-9]+", text)
            matched = {term for term in terms if any(token.startswith(term) for token in tokens)}
            if len(matched) >= min(MIN_MATCHED_SEARCH_TERMS, len(set(terms))):
                results.append({
                    "article_id": row["article_id"],
                    "title": row["title"],
                    "content": row["content"],
                    "source": row["source"],
                })
            if len(results) == MAX_KNOWLEDGE_RESULTS:
                break
        return {"ok": True, "found": bool(results), "results": results}
    except sqlite3.Error:
        LOGGER.exception("Knowledge base search failed")
        return _tool_error("The knowledge base is temporarily unavailable.")
    finally:
        if conn is not None:
            conn.close()


def lookup_ticket(
    ticket_id: str | None = None,
    employee_id: str | None = None,
    issue_summary: str | None = None,
) -> dict:
    """Look up a ticket by ID or by employee plus issue text."""
    if not ticket_id and not issue_summary:
        return _tool_error("A ticket ID or issue description is required.")

    conn = None
    try:
        conn = get_read_only_connection()
        if ticket_id:
            row = conn.execute(
                "SELECT * FROM support_tickets WHERE ticket_id = ?", (ticket_id,)
            ).fetchone()
            if row is not None and employee_id and row["employee_id"] != employee_id:
                row = None
        else:
            rows = conn.execute(
                "SELECT * FROM support_tickets"
                + (" WHERE employee_id = ?" if employee_id else "")
                + " ORDER BY created_at DESC",
                (employee_id,) if employee_id else (),
            ).fetchall()
            query_terms = {
                term
                for term in re.findall(r"[a-z0-9]+", issue_summary.lower())
                if len(term) >= MIN_SEARCH_TOKEN_LENGTH
            }
            ranked = []
            for candidate in rows:
                candidate_terms = set(
                    re.findall(r"[a-z0-9]+", candidate["issue_summary"].lower())
                )
                overlap = {
                    term
                    for term in query_terms
                    if any(token.startswith(term) or term.startswith(token) for token in candidate_terms)
                }
                if overlap:
                    ranked.append((len(overlap), candidate))
            row = max(ranked, key=lambda item: item[0])[1] if ranked else None
    except sqlite3.Error:
        LOGGER.exception("Ticket lookup failed")
        return _tool_error("The ticket database is temporarily unavailable.")
    finally:
        if conn is not None:
            conn.close()
    if row is None:
        return {"ok": True, "found": False, "ticket_id": ticket_id}
    return {"ok": True, "found": True, "ticket": dict(row)}


def create_ticket(
    employee_id: str,
    issue_summary: str,
    category: str = DEFAULT_CATEGORY,
    priority: str = DEFAULT_PRIORITY,
) -> dict:
    """Create a ticket after checking the employee and open duplicates."""
    if not employee_id or not issue_summary.strip():
        return {"created": False, "error": "Employee ID and issue description are required."}
    if priority not in SUPPORTED_PRIORITIES:
        return {"created": False, "error": "Priority must be low, medium, high, or critical."}

    conn = None
    try:
        ensure_initialized()
        conn = get_admin_connection()
        employee = conn.execute(
            "SELECT employee_id FROM employees WHERE employee_id = ?", (employee_id,)
        ).fetchone()
        if employee is None:
            return {"ok": True, "created": False, "error": f"Employee {employee_id} was not found."}
        duplicate = conn.execute(
            "SELECT ticket_id FROM support_tickets "
            "WHERE employee_id = ? AND status IN (?, ?) AND lower(issue_summary) = lower(?)",
            (employee_id, *ACTIVE_TICKET_STATUSES, issue_summary.strip()),
        ).fetchone()
        if duplicate:
            return {
                "ok": True,
                "created": False,
                "duplicate": True,
                "ticket_id": duplicate["ticket_id"],
                "error": "A matching open ticket already exists.",
            }
        ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"
        conn.execute(
            "INSERT INTO support_tickets "
            "(ticket_id, employee_id, issue_summary, category, priority, status, created_at) "
            "VALUES (?, ?, ?, ?, ?, 'open', ?)",
            (
                ticket_id,
                employee_id,
                issue_summary.strip(),
                category,
                priority,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()
        return {"ok": True, "created": True, "ticket_id": ticket_id, "status": "open"}
    except sqlite3.Error:
        if conn is not None:
            conn.rollback()
        LOGGER.exception("Ticket creation failed")
        return _tool_error("The ticket database is temporarily unavailable.")
    finally:
        if conn is not None:
            conn.close()
